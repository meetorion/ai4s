package api

import (
	"net/http"
	
	"github.com/gin-gonic/gin"
	"iot-platform-backend/internal/api/controllers"
	"iot-platform-backend/internal/middleware"
	"iot-platform-backend/internal/websocket"
	"iot-platform-backend/internal/database"
)

// SetupRoutes 设置所有API路由
func SetupRoutes(r *gin.Engine) {
	// 创建控制器实例
	authController := controllers.NewAuthController()
	deviceController := controllers.NewDeviceController()
	projectController := controllers.NewProjectController()
	
	// 全局中间件
	r.Use(middleware.CORS())
	r.Use(middleware.RequestID())
	r.Use(middleware.Logger())
	
	// 健康检查路由（无需认证）
	r.GET("/health", healthCheck)
	r.GET("/metrics", metricsHandler)
	
	// API版本前缀
	v1 := r.Group("/api/v1")
	
	// 认证路由（无需认证）
	auth := v1.Group("/auth")
	{
		auth.POST("/login", authController.Login)
		auth.POST("/register", authController.Register)
		auth.POST("/refresh", authController.RefreshToken)
		
		// 需要认证的认证路由
		authProtected := auth.Group("")
		authProtected.Use(middleware.AuthRequired())
		{
			authProtected.GET("/me", authController.Me)
			authProtected.POST("/logout", authController.Logout)
			authProtected.PUT("/password", authController.ChangePassword)
		}
	}
	
	// WebSocket路由（支持可选认证）
	v1.GET("/ws", middleware.OptionalAuth(), websocket.HandleWebSocket)
	
	// 设备路由
	devices := v1.Group("/devices")
	{
		// 公开路由
		devices.GET("/types", deviceController.GetDeviceTypes)
		
		// 设备数据上报（IoT设备使用，可能需要不同的认证方式）
		devices.POST("/:device_id/data", deviceController.PostDeviceData)
		
		// 需要用户认证的路由
		devicesProtected := devices.Group("")
		devicesProtected.Use(middleware.AuthRequired())
		{
			devicesProtected.GET("", deviceController.GetDevices)
			devicesProtected.POST("", deviceController.CreateDevice)
			devicesProtected.GET("/stats", deviceController.GetDeviceStats)
			devicesProtected.GET("/:id", deviceController.GetDevice)
			devicesProtected.PUT("/:id", deviceController.UpdateDevice)
			devicesProtected.DELETE("/:id", deviceController.DeleteDevice)
			devicesProtected.GET("/:device_id/data", deviceController.GetDeviceData)
			devicesProtected.GET("/:device_id/history", deviceController.GetDeviceHistory)
		}
	}
	
	// 项目路由
	projects := v1.Group("/projects")
	{
		// 需要认证的路由
		projectsProtected := projects.Group("")
		projectsProtected.Use(middleware.AuthRequired())
		{
			projectsProtected.GET("", projectController.GetProjects)
			projectsProtected.POST("", projectController.CreateProject)
			projectsProtected.GET("/:id", projectController.GetProject)
			projectsProtected.PUT("/:id", projectController.UpdateProject)
			projectsProtected.DELETE("/:id", projectController.DeleteProject)
			
			// Fork功能
			projectsProtected.POST("/:id/fork", projectController.ForkProject)
			projectsProtected.POST("/:id/star", projectController.StarProject)
			
			// 项目历史
			projectsProtected.GET("/:id/history", projectController.GetProjectHistory)
		}
	}
	
	// 用户管理路由（管理员专用）
	admin := v1.Group("/admin")
	admin.Use(middleware.AuthRequired())
	admin.Use(middleware.AdminRequired())
	{
		// 用户管理
		admin.GET("/users", getUserList)
		admin.GET("/users/:id", getUserDetail)
		admin.PUT("/users/:id/status", updateUserStatus)
		
		// 系统统计
		admin.GET("/stats", getSystemStats)
		
		// 系统配置
		admin.GET("/config", getSystemConfig)
		admin.PUT("/config", updateSystemConfig)
	}
	
	// 文件上传路由
	upload := v1.Group("/upload")
	upload.Use(middleware.AuthRequired())
	{
		upload.POST("/avatar", uploadAvatar)
		upload.POST("/file", uploadFile)
	}
	
	// 公开API（支持CORS，用于前端调用）
	public := v1.Group("/public")
	{
		public.GET("/projects", publicProjectList)
		public.GET("/projects/:id", publicProjectDetail)
		public.GET("/stats", publicStats)
	}
}

// healthCheck 健康检查
func healthCheck(c *gin.Context) {
	// 检查数据库连接
	dbHealth := "ok"
	if err := database.Health(); err != nil {
		dbHealth = "error: " + err.Error()
	}
	
	// 检查Redis连接
	redisHealth := "ok"
	if err := database.RedisHealth(); err != nil {
		redisHealth = "error: " + err.Error()
	}
	
	// 检查WebSocket管理器
	wsHealth := "ok"
	wsConnections := 0
	if websocket.DefaultManager != nil {
		wsConnections = websocket.DefaultManager.GetClientCount()
	} else {
		wsHealth = "not initialized"
	}
	
	status := http.StatusOK
	if dbHealth != "ok" || redisHealth != "ok" {
		status = http.StatusServiceUnavailable
	}
	
	c.JSON(status, gin.H{
		"status": "healthy",
		"timestamp": gin.H{
			"unix": gin.H{
				"timestamp": gin.H{},
			},
		},
		"checks": gin.H{
			"database":    dbHealth,
			"redis":       redisHealth,
			"websocket":   wsHealth,
			"connections": wsConnections,
		},
	})
}

// metricsHandler 指标处理器
func metricsHandler(c *gin.Context) {
	// 获取数据库统计
	dbStats, _ := database.Stats()
	
	// 获取Redis统计
	redisStats, _ := database.RedisStats()
	
	c.JSON(http.StatusOK, gin.H{
		"database":  dbStats,
		"redis":     redisStats,
		"websocket": gin.H{
			"connections": websocket.DefaultManager.GetClientCount(),
		},
	})
}

// 临时占位处理器（待实现）
func getUserList(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"status": 1,
		"data":   []interface{}{},
		"msg":    "功能开发中",
	})
}

func getUserDetail(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"status": 1,
		"data":   nil,
		"msg":    "功能开发中",
	})
}

func updateUserStatus(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"status": 1,
		"msg":    "功能开发中",
	})
}

func getSystemStats(c *gin.Context) {
	// 获取基本统计信息
	db := database.GetDB()
	
	var userCount, deviceCount, projectCount int64
	db.Model(&models.User{}).Count(&userCount)
	db.Model(&models.Device{}).Count(&deviceCount)
	db.Model(&models.Project{}).Count(&projectCount)
	
	c.JSON(http.StatusOK, gin.H{
		"status": 1,
		"data": gin.H{
			"users":    userCount,
			"devices":  deviceCount,
			"projects": projectCount,
		},
	})
}

func getSystemConfig(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"status": 1,
		"data":   nil,
		"msg":    "功能开发中",
	})
}

func updateSystemConfig(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"status": 1,
		"msg":    "功能开发中",
	})
}

func uploadAvatar(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"status": 1,
		"msg":    "功能开发中",
	})
}

func uploadFile(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"status": 1,
		"msg":    "功能开发中",
	})
}

func publicProjectList(c *gin.Context) {
	// 获取公开项目列表
	db := database.GetDB()
	var projects []models.Project
	
	db.Where("public = ?", true).
		Preload("Owner").
		Order("star_count DESC, created_at DESC").
		Limit(20).
		Find(&projects)
	
	c.JSON(http.StatusOK, gin.H{
		"status": 1,
		"data":   projects,
	})
}

func publicProjectDetail(c *gin.Context) {
	projectID := c.Param("id")
	
	db := database.GetDB()
	var project models.Project
	
	if err := db.Where("id = ? AND public = ?", projectID, true).
		Preload("Owner").
		First(&project).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{
			"error": "Project not found",
		})
		return
	}
	
	c.JSON(http.StatusOK, gin.H{
		"status": 1,
		"data":   project,
	})
}

func publicStats(c *gin.Context) {
	db := database.GetDB()
	
	var stats struct {
		PublicProjects int64 `json:"public_projects"`
		TotalViews     int64 `json:"total_views"`
		TotalStars     int64 `json:"total_stars"`
		ActiveUsers    int64 `json:"active_users"`
	}
	
	db.Model(&models.Project{}).Where("public = ?", true).Count(&stats.PublicProjects)
	db.Model(&models.Project{}).Select("COALESCE(SUM(view_count), 0)").Row().Scan(&stats.TotalViews)
	db.Model(&models.Project{}).Select("COALESCE(SUM(star_count), 0)").Row().Scan(&stats.TotalStars)
	
	// 活跃用户：最近30天有活动的用户
	//thirtyDaysAgo := time.Now().AddDate(0, 0, -30)
	//db.Model(&models.User{}).Where("last_login > ?", thirtyDaysAgo).Count(&stats.ActiveUsers)
	
	c.JSON(http.StatusOK, gin.H{
		"status": 1,
		"data":   stats,
	})
}