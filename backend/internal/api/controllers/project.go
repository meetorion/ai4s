package controllers

import (
	"net/http"
	"strconv"
	"time"
	
	"github.com/gin-gonic/gin"
	"iot-platform-backend/internal/database"
	"iot-platform-backend/internal/middleware"
	"iot-platform-backend/internal/models"
	"github.com/lib/pq"
)

// ProjectController 项目控制器
type ProjectController struct{}

// NewProjectController 创建项目控制器
func NewProjectController() *ProjectController {
	return &ProjectController{}
}

// CreateProjectRequest 创建项目请求
type CreateProjectRequest struct {
	Name        string         `json:"name" binding:"required"`
	Description string         `json:"description"`
	Config      models.JSONB   `json:"config"`
	Public      bool           `json:"public"`
	Tags        []string       `json:"tags"`
}

// UpdateProjectRequest 更新项目请求
type UpdateProjectRequest struct {
	Name        string       `json:"name"`
	Description string       `json:"description"`
	Config      models.JSONB `json:"config"`
	Public      bool         `json:"public"`
	Tags        []string     `json:"tags"`
}

// ForkProjectRequest Fork项目请求
type ForkProjectRequest struct {
	Name        string       `json:"name"`
	Description string       `json:"description"`
	Message     string       `json:"message"`
	Config      models.JSONB `json:"config"`
}

// ProjectListResponse 项目列表响应
type ProjectListResponse struct {
	Projects []models.Project `json:"projects"`
	Total    int64            `json:"total"`
	Page     int              `json:"page"`
	Limit    int              `json:"limit"`
}

// GetProjects 获取项目列表
// @Summary 获取项目列表
// @Description 获取用户的项目列表，支持分页和筛选
// @Tags 项目管理
// @Security BearerAuth
// @Produce json
// @Param page query int false "页码" default(1)
// @Param limit query int false "每页数量" default(10)
// @Param public query bool false "是否只显示公开项目"
// @Param tag query string false "标签筛选"
// @Success 200 {object} ProjectListResponse
// @Router /projects [get]
func (ctrl *ProjectController) GetProjects(c *gin.Context) {
	userID := middleware.GetUserID(c)
	isAdmin := middleware.IsAdmin(c)
	
	// 解析分页参数
	page, _ := strconv.Atoi(c.DefaultQuery("page", "1"))
	limit, _ := strconv.Atoi(c.DefaultQuery("limit", "10"))
	if page < 1 {
		page = 1
	}
	if limit < 1 || limit > 100 {
		limit = 10
	}
	
	offset := (page - 1) * limit
	
	// 构建查询
	db := database.GetDB()
	query := db.Model(&models.Project{}).Preload("Owner")
	
	// 筛选条件
	publicOnly := c.Query("public") == "true"
	if publicOnly {
		query = query.Where("public = ?", true)
	} else if !isAdmin {
		// 非管理员只能看到自己的项目或公开项目
		query = query.Where("owner_id = ? OR public = ?", userID, true)
	}
	
	// 标签筛选
	if tag := c.Query("tag"); tag != "" {
		query = query.Where("? = ANY(tags)", tag)
	}
	
	// 关键词搜索
	if search := c.Query("search"); search != "" {
		query = query.Where("name ILIKE ? OR description ILIKE ?", "%"+search+"%", "%"+search+"%")
	}
	
	var total int64
	var projects []models.Project
	
	// 获取总数
	query.Count(&total)
	
	// 获取项目列表
	if err := query.Offset(offset).Limit(limit).Order("created_at DESC").Find(&projects).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "Failed to fetch projects",
		})
		return
	}
	
	response := ProjectListResponse{
		Projects: projects,
		Total:    total,
		Page:     page,
		Limit:    limit,
	}
	
	c.JSON(http.StatusOK, gin.H{
		"status": 1,
		"data":   response,
	})
}

// GetProject 获取项目详情
// @Summary 获取项目详情
// @Description 根据ID获取项目的详细信息
// @Tags 项目管理
// @Security BearerAuth
// @Produce json
// @Param id path int true "项目ID"
// @Success 200 {object} models.Project
// @Failure 404 {object} map[string]interface{}
// @Router /projects/{id} [get]
func (ctrl *ProjectController) GetProject(c *gin.Context) {
	userID := middleware.GetUserID(c)
	projectID, err := strconv.ParseUint(c.Param("id"), 10, 32)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "Invalid project ID",
		})
		return
	}
	
	db := database.GetDB()
	var project models.Project
	
	// 查询项目（包含关联数据）
	query := db.Preload("Owner").Preload("Parent").Preload("Children")
	if err := query.First(&project, uint(projectID)).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{
			"error": "Project not found",
		})
		return
	}
	
	// 权限检查：只有项目拥有者、管理员或公开项目才能访问
	if project.OwnerID != userID && !project.Public && !middleware.IsAdmin(c) {
		c.JSON(http.StatusForbidden, gin.H{
			"error": "Access denied",
		})
		return
	}
	
	// 增加查看次数
	if project.OwnerID != userID { // 不统计自己查看自己项目的次数
		go func() {
			db.Model(&project).Update("view_count", project.ViewCount+1)
		}()
	}
	
	c.JSON(http.StatusOK, gin.H{
		"status": 1,
		"data":   project,
	})
}

// CreateProject 创建项目
// @Summary 创建新项目
// @Description 创建一个新的可视化项目
// @Tags 项目管理
// @Security BearerAuth
// @Accept json
// @Produce json
// @Param request body CreateProjectRequest true "项目信息"
// @Success 201 {object} models.Project
// @Failure 400 {object} map[string]interface{}
// @Router /projects [post]
func (ctrl *ProjectController) CreateProject(c *gin.Context) {
	userID := middleware.GetUserID(c)
	if userID == 0 {
		c.JSON(http.StatusUnauthorized, gin.H{
			"error": "Authentication required",
		})
		return
	}
	
	var req CreateProjectRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error":   "Invalid request format",
			"details": err.Error(),
		})
		return
	}
	
	// 创建项目
	project := models.Project{
		Name:        req.Name,
		Description: req.Description,
		Config:      req.Config,
		Public:      req.Public,
		Tags:        pq.StringArray(req.Tags),
		OwnerID:     userID,
	}
	
	db := database.GetDB()
	if err := db.Create(&project).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "Failed to create project",
		})
		return
	}
	
	// 记录创建历史
	history := models.ForkHistory{
		ProjectID: project.ID,
		UserID:    userID,
		Action:    "create",
		Message:   "项目创建",
		IPAddress: c.ClientIP(),
		UserAgent: c.GetHeader("User-Agent"),
	}
	db.Create(&history)
	
	// 加载关联数据返回
	db.Preload("Owner").First(&project, project.ID)
	
	c.JSON(http.StatusCreated, gin.H{
		"status": 1,
		"msg":    "项目创建成功",
		"data":   project,
	})
}

// UpdateProject 更新项目
// @Summary 更新项目
// @Description 更新项目信息
// @Tags 项目管理
// @Security BearerAuth
// @Accept json
// @Produce json
// @Param id path int true "项目ID"
// @Param request body UpdateProjectRequest true "更新信息"
// @Success 200 {object} models.Project
// @Failure 400 {object} map[string]interface{}
// @Router /projects/{id} [put]
func (ctrl *ProjectController) UpdateProject(c *gin.Context) {
	userID := middleware.GetUserID(c)
	projectID, err := strconv.ParseUint(c.Param("id"), 10, 32)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "Invalid project ID",
		})
		return
	}
	
	var req UpdateProjectRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error":   "Invalid request format",
			"details": err.Error(),
		})
		return
	}
	
	db := database.GetDB()
	var project models.Project
	
	// 查询项目并验证所有权
	if err := db.First(&project, uint(projectID)).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{
			"error": "Project not found",
		})
		return
	}
	
	if project.OwnerID != userID && !middleware.IsAdmin(c) {
		c.JSON(http.StatusForbidden, gin.H{
			"error": "Access denied",
		})
		return
	}
	
	// 保存更新前的配置（用于diff）
	oldConfig := project.Config
	
	// 更新项目信息
	if req.Name != "" {
		project.Name = req.Name
	}
	project.Description = req.Description
	if req.Config != nil {
		project.Config = req.Config
	}
	project.Public = req.Public
	if req.Tags != nil {
		project.Tags = pq.StringArray(req.Tags)
	}
	
	if err := db.Save(&project).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "Failed to update project",
		})
		return
	}
	
	// 记录更新历史
	configDiff := make(models.JSONB)
	configDiff["old"] = oldConfig
	configDiff["new"] = project.Config
	
	history := models.ForkHistory{
		ProjectID:  project.ID,
		UserID:     userID,
		Action:     "update",
		ConfigDiff: configDiff,
		Message:    "项目配置更新",
		IPAddress:  c.ClientIP(),
		UserAgent:  c.GetHeader("User-Agent"),
	}
	db.Create(&history)
	
	// 清除缓存
	cache := database.NewCache()
	cache.Delete(c, database.Keys.Project(project.ID))
	
	c.JSON(http.StatusOK, gin.H{
		"status": 1,
		"msg":    "项目更新成功",
		"data":   project,
	})
}

// DeleteProject 删除项目
// @Summary 删除项目
// @Description 删除指定项目
// @Tags 项目管理
// @Security BearerAuth
// @Produce json
// @Param id path int true "项目ID"
// @Success 200 {object} map[string]interface{}
// @Failure 404 {object} map[string]interface{}
// @Router /projects/{id} [delete]
func (ctrl *ProjectController) DeleteProject(c *gin.Context) {
	userID := middleware.GetUserID(c)
	projectID, err := strconv.ParseUint(c.Param("id"), 10, 32)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "Invalid project ID",
		})
		return
	}
	
	db := database.GetDB()
	var project models.Project
	
	// 查询项目并验证所有权
	if err := db.First(&project, uint(projectID)).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{
			"error": "Project not found",
		})
		return
	}
	
	if project.OwnerID != userID && !middleware.IsAdmin(c) {
		c.JSON(http.StatusForbidden, gin.H{
			"error": "Access denied",
		})
		return
	}
	
	// 在事务中删除项目及相关数据
	err = database.Transaction(func(tx *database.DB) error {
		// 删除Fork历史记录
		tx.Where("project_id = ?", project.ID).Delete(&models.ForkHistory{})
		
		// 删除点赞记录
		tx.Where("project_id = ?", project.ID).Delete(&models.ProjectStar{})
		
		// 删除Fork记录
		tx.Where("project_id = ?", project.ID).Delete(&models.Fork{})
		
		// 删除项目
		return tx.Delete(&project).Error
	})
	
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "Failed to delete project",
		})
		return
	}
	
	c.JSON(http.StatusOK, gin.H{
		"status": 1,
		"msg":    "项目删除成功",
	})
}

// ForkProject Fork项目
// @Summary Fork项目
// @Description 创建项目的一个分支副本
// @Tags 项目管理
// @Security BearerAuth
// @Accept json
// @Produce json
// @Param id path int true "源项目ID"
// @Param request body ForkProjectRequest true "Fork信息"
// @Success 201 {object} models.Project
// @Failure 400 {object} map[string]interface{}
// @Router /projects/{id}/fork [post]
func (ctrl *ProjectController) ForkProject(c *gin.Context) {
	userID := middleware.GetUserID(c)
	if userID == 0 {
		c.JSON(http.StatusUnauthorized, gin.H{
			"error": "Authentication required",
		})
		return
	}
	
	sourceID, err := strconv.ParseUint(c.Param("id"), 10, 32)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "Invalid project ID",
		})
		return
	}
	
	var req ForkProjectRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error":   "Invalid request format",
			"details": err.Error(),
		})
		return
	}
	
	db := database.GetDB()
	var sourceProject models.Project
	
	// 查询源项目
	if err := db.First(&sourceProject, uint(sourceID)).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{
			"error": "Source project not found",
		})
		return
	}
	
	// 权限检查：只有公开项目或拥有者才能Fork
	if !sourceProject.Public && sourceProject.OwnerID != userID && !middleware.IsAdmin(c) {
		c.JSON(http.StatusForbidden, gin.H{
			"error": "Cannot fork private project",
		})
		return
	}
	
	// 检查是否已经Fork过
	var existingFork models.Project
	if err := db.Where("parent_id = ? AND owner_id = ?", sourceProject.ID, userID).First(&existingFork).Error; err == nil {
		c.JSON(http.StatusConflict, gin.H{
			"error": "You have already forked this project",
			"data":  existingFork,
		})
		return
	}
	
	// 创建Fork项目
	var forkConfig models.JSONB
	if req.Config != nil {
		forkConfig = req.Config
	} else {
		forkConfig = sourceProject.Config
	}
	
	forkProject := models.Project{
		Name:        req.Name,
		Description: req.Description,
		ParentID:    &sourceProject.ID,
		Config:      forkConfig,
		Public:      false, // Fork的项目默认为私有
		Tags:        sourceProject.Tags,
		OwnerID:     userID,
	}
	
	err = database.Transaction(func(tx *database.DB) error {
		// 创建Fork项目
		if err := tx.Create(&forkProject).Error; err != nil {
			return err
		}
		
		// 创建Fork记录
		fork := models.Fork{
			ProjectID: forkProject.ID,
			UserID:    userID,
			Config:    sourceProject.Config,
			Message:   req.Message,
		}
		if err := tx.Create(&fork).Error; err != nil {
			return err
		}
		
		// 增加源项目的Fork数量
		sourceProject.IncrementForkCount()
		if err := tx.Save(&sourceProject).Error; err != nil {
			return err
		}
		
		// 记录Fork历史
		history := models.ForkHistory{
			ProjectID:  forkProject.ID,
			UserID:     userID,
			Action:     "fork",
			ConfigDiff: models.JSONB{"source_id": sourceProject.ID},
			Message:    req.Message,
			IPAddress:  c.ClientIP(),
			UserAgent:  c.GetHeader("User-Agent"),
		}
		return tx.Create(&history).Error
	})
	
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "Failed to fork project",
		})
		return
	}
	
	// 加载关联数据返回
	db.Preload("Owner").Preload("Parent").First(&forkProject, forkProject.ID)
	
	c.JSON(http.StatusCreated, gin.H{
		"status": 1,
		"msg":    "Fork创建成功",
		"data":   forkProject,
	})
}

// StarProject 给项目点赞
// @Summary 给项目点赞/取消点赞
// @Description 给项目点赞或取消点赞
// @Tags 项目管理
// @Security BearerAuth
// @Produce json
// @Param id path int true "项目ID"
// @Success 200 {object} map[string]interface{}
// @Router /projects/{id}/star [post]
func (ctrl *ProjectController) StarProject(c *gin.Context) {
	userID := middleware.GetUserID(c)
	if userID == 0 {
		c.JSON(http.StatusUnauthorized, gin.H{
			"error": "Authentication required",
		})
		return
	}
	
	projectID, err := strconv.ParseUint(c.Param("id"), 10, 32)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "Invalid project ID",
		})
		return
	}
	
	db := database.GetDB()
	var project models.Project
	
	// 验证项目存在且有权访问
	if err := db.First(&project, uint(projectID)).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{
			"error": "Project not found",
		})
		return
	}
	
	if !project.Public && project.OwnerID != userID && !middleware.IsAdmin(c) {
		c.JSON(http.StatusForbidden, gin.H{
			"error": "Access denied",
		})
		return
	}
	
	// 检查是否已经点赞
	var existingStar models.ProjectStar
	if err := db.Where("project_id = ? AND user_id = ?", project.ID, userID).First(&existingStar).Error; err == nil {
		// 已经点赞，取消点赞
		db.Delete(&existingStar)
		project.StarCount--
		db.Save(&project)
		
		c.JSON(http.StatusOK, gin.H{
			"status":  1,
			"msg":     "取消点赞成功",
			"starred": false,
			"count":   project.StarCount,
		})
		return
	}
	
	// 创建点赞记录
	star := models.ProjectStar{
		ProjectID: project.ID,
		UserID:    userID,
	}
	
	if err := db.Create(&star).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "Failed to star project",
		})
		return
	}
	
	// 增加点赞数
	project.StarCount++
	db.Save(&project)
	
	c.JSON(http.StatusOK, gin.H{
		"status":  1,
		"msg":     "点赞成功",
		"starred": true,
		"count":   project.StarCount,
	})
}

// GetProjectHistory 获取项目历史记录
// @Summary 获取项目历史记录
// @Description 获取项目的操作历史记录
// @Tags 项目管理
// @Security BearerAuth
// @Produce json
// @Param id path int true "项目ID"
// @Success 200 {object} []models.ForkHistory
// @Router /projects/{id}/history [get]
func (ctrl *ProjectController) GetProjectHistory(c *gin.Context) {
	userID := middleware.GetUserID(c)
	projectID, err := strconv.ParseUint(c.Param("id"), 10, 32)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "Invalid project ID",
		})
		return
	}
	
	db := database.GetDB()
	var project models.Project
	
	// 验证项目存在且有权访问
	if err := db.First(&project, uint(projectID)).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{
			"error": "Project not found",
		})
		return
	}
	
	if project.OwnerID != userID && !middleware.IsAdmin(c) {
		c.JSON(http.StatusForbidden, gin.H{
			"error": "Access denied",
		})
		return
	}
	
	var history []models.ForkHistory
	if err := db.Where("project_id = ?", project.ID).
		Preload("User").
		Order("created_at DESC").
		Find(&history).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "Failed to fetch project history",
		})
		return
	}
	
	c.JSON(http.StatusOK, gin.H{
		"status": 1,
		"data":   history,
	})
}