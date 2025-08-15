package controllers

import (
	"net/http"
	"strings"
	"time"
	
	"github.com/gin-gonic/gin"
	"iot-platform-backend/internal/database"
	"iot-platform-backend/internal/middleware"
	"iot-platform-backend/internal/models"
)

// AuthController 认证控制器
type AuthController struct{}

// NewAuthController 创建认证控制器
func NewAuthController() *AuthController {
	return &AuthController{}
}

// LoginRequest 登录请求结构
type LoginRequest struct {
	Username string `json:"username" binding:"required"`
	Password string `json:"password" binding:"required"`
}

// RegisterRequest 注册请求结构
type RegisterRequest struct {
	Username string `json:"username" binding:"required,min=3,max=50"`
	Email    string `json:"email" binding:"omitempty,email"`
	Phone    string `json:"phone" binding:"omitempty"`
	Password string `json:"password" binding:"required,min=6"`
}

// LoginResponse 登录响应结构
type LoginResponse struct {
	User         UserInfo `json:"user"`
	AccessToken  string   `json:"access_token"`
	RefreshToken string   `json:"refresh_token"`
	ExpiresIn    int64    `json:"expires_in"`
}

// UserInfo 用户信息结构
type UserInfo struct {
	ID       uint   `json:"id"`
	Username string `json:"username"`
	Email    string `json:"email"`
	Phone    string `json:"phone"`
	Avatar   string `json:"avatar"`
	Role     string `json:"role"`
	Active   bool   `json:"active"`
}

// Login 用户登录
// @Summary 用户登录
// @Description 用户登录接口，支持用户名/邮箱/手机号登录
// @Tags 认证
// @Accept json
// @Produce json
// @Param request body LoginRequest true "登录信息"
// @Success 200 {object} LoginResponse
// @Failure 400 {object} map[string]interface{}
// @Failure 401 {object} map[string]interface{}
// @Router /auth/login [post]
func (ctrl *AuthController) Login(c *gin.Context) {
	var req LoginRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error":   "Invalid request format",
			"details": err.Error(),
		})
		return
	}
	
	db := database.GetDB()
	var user models.User
	
	// 支持用户名、邮箱或手机号登录
	query := db.Where("username = ? OR email = ? OR phone = ?", 
		req.Username, req.Username, req.Username)
	
	if err := query.First(&user).Error; err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{
			"error": "Invalid credentials",
		})
		return
	}
	
	// 检查账户是否激活
	if !user.Active {
		c.JSON(http.StatusUnauthorized, gin.H{
			"error": "Account is deactivated",
		})
		return
	}
	
	// 验证密码
	if !user.CheckPassword(req.Password) {
		c.JSON(http.StatusUnauthorized, gin.H{
			"error": "Invalid credentials",
		})
		return
	}
	
	// 生成JWT token
	accessToken, err := middleware.GenerateToken(user.ID, user.Username, user.Role)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "Failed to generate token",
		})
		return
	}
	
	refreshToken, err := middleware.GenerateRefreshToken(user.ID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "Failed to generate refresh token",
		})
		return
	}
	
	// 更新最后登录时间
	user.UpdateLastLogin(db)
	
	// 缓存用户信息
	cache := database.NewCache()
	cache.Set(c, database.Keys.User(user.ID), &user, 1*time.Hour)
	
	response := LoginResponse{
		User: UserInfo{
			ID:       user.ID,
			Username: user.Username,
			Email:    user.Email,
			Phone:    user.Phone,
			Avatar:   user.Avatar,
			Role:     user.Role,
			Active:   user.Active,
		},
		AccessToken:  accessToken,
		RefreshToken: refreshToken,
		ExpiresIn:    int64(time.Hour * 24 / time.Second), // 24小时，转换为秒
	}
	
	c.JSON(http.StatusOK, gin.H{
		"status": 1,
		"msg":    "登录成功",
		"data":   response,
	})
}

// Register 用户注册
// @Summary 用户注册
// @Description 新用户注册接口
// @Tags 认证
// @Accept json
// @Produce json
// @Param request body RegisterRequest true "注册信息"
// @Success 201 {object} UserInfo
// @Failure 400 {object} map[string]interface{}
// @Failure 409 {object} map[string]interface{}
// @Router /auth/register [post]
func (ctrl *AuthController) Register(c *gin.Context) {
	var req RegisterRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error":   "Invalid request format",
			"details": err.Error(),
		})
		return
	}
	
	db := database.GetDB()
	
	// 检查用户名是否已存在
	var existingUser models.User
	if err := db.Where("username = ?", req.Username).First(&existingUser).Error; err == nil {
		c.JSON(http.StatusConflict, gin.H{
			"error": "Username already exists",
		})
		return
	}
	
	// 检查邮箱是否已存在
	if req.Email != "" {
		if err := db.Where("email = ?", req.Email).First(&existingUser).Error; err == nil {
			c.JSON(http.StatusConflict, gin.H{
				"error": "Email already exists",
			})
			return
		}
	}
	
	// 检查手机号是否已存在
	if req.Phone != "" {
		if err := db.Where("phone = ?", req.Phone).First(&existingUser).Error; err == nil {
			c.JSON(http.StatusConflict, gin.H{
				"error": "Phone number already exists",
			})
			return
		}
	}
	
	// 创建新用户
	user := models.User{
		Username: req.Username,
		Email:    req.Email,
		Phone:    req.Phone,
		Password: req.Password, // 会在BeforeCreate中自动加密
		Role:     "user",
		Active:   true,
	}
	
	if err := db.Create(&user).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "Failed to create user",
		})
		return
	}
	
	userInfo := UserInfo{
		ID:       user.ID,
		Username: user.Username,
		Email:    user.Email,
		Phone:    user.Phone,
		Avatar:   user.Avatar,
		Role:     user.Role,
		Active:   user.Active,
	}
	
	c.JSON(http.StatusCreated, gin.H{
		"status": 1,
		"msg":    "注册成功",
		"data":   userInfo,
	})
}

// RefreshToken 刷新访问令牌
// @Summary 刷新访问令牌
// @Description 使用刷新令牌获取新的访问令牌
// @Tags 认证
// @Accept json
// @Produce json
// @Param Authorization header string true "Bearer refresh_token"
// @Success 200 {object} map[string]interface{}
// @Failure 401 {object} map[string]interface{}
// @Router /auth/refresh [post]
func (ctrl *AuthController) RefreshToken(c *gin.Context) {
	refreshToken := extractTokenFromHeader(c)
	if refreshToken == "" {
		c.JSON(http.StatusUnauthorized, gin.H{
			"error": "Missing refresh token",
		})
		return
	}
	
	// TODO: 实现refresh token解析和验证逻辑
	// 这里需要解析refresh token并生成新的access token
	
	c.JSON(http.StatusOK, gin.H{
		"access_token": "new_access_token",
		"expires_in":   3600,
	})
}

// Logout 用户登出
// @Summary 用户登出
// @Description 用户登出，将token加入黑名单
// @Tags 认证
// @Security BearerAuth
// @Success 200 {object} map[string]interface{}
// @Router /auth/logout [post]
func (ctrl *AuthController) Logout(c *gin.Context) {
	// 获取当前token
	token := extractTokenFromHeader(c)
	if token != "" {
		// TODO: 将token加入Redis黑名单
		cache := database.NewCache()
		cache.Set(c, "blacklist:"+token, true, 24*time.Hour)
	}
	
	c.JSON(http.StatusOK, gin.H{
		"status": 1,
		"msg":    "登出成功",
	})
}

// Me 获取当前用户信息
// @Summary 获取当前用户信息
// @Description 获取当前认证用户的详细信息
// @Tags 认证
// @Security BearerAuth
// @Produce json
// @Success 200 {object} UserInfo
// @Failure 401 {object} map[string]interface{}
// @Router /auth/me [get]
func (ctrl *AuthController) Me(c *gin.Context) {
	userID, username, role, authenticated := middleware.GetCurrentUser(c)
	if !authenticated {
		c.JSON(http.StatusUnauthorized, gin.H{
			"error": "Authentication required",
		})
		return
	}
	
	// 先尝试从缓存获取
	cache := database.NewCache()
	var user models.User
	
	if err := cache.Get(c, database.Keys.User(userID), &user); err != nil {
		// 缓存未命中，从数据库获取
		db := database.GetDB()
		if err := db.First(&user, userID).Error; err != nil {
			c.JSON(http.StatusNotFound, gin.H{
				"error": "User not found",
			})
			return
		}
		
		// 更新缓存
		cache.Set(c, database.Keys.User(userID), &user, 1*time.Hour)
	}
	
	userInfo := UserInfo{
		ID:       user.ID,
		Username: user.Username,
		Email:    user.Email,
		Phone:    user.Phone,
		Avatar:   user.Avatar,
		Role:     user.Role,
		Active:   user.Active,
	}
	
	c.JSON(http.StatusOK, gin.H{
		"status": 1,
		"data":   userInfo,
	})
}

// ChangePassword 修改密码
// @Summary 修改密码
// @Description 修改当前用户密码
// @Tags 认证
// @Security BearerAuth
// @Accept json
// @Produce json
// @Param request body ChangePasswordRequest true "密码修改信息"
// @Success 200 {object} map[string]interface{}
// @Failure 400 {object} map[string]interface{}
// @Router /auth/password [put]
func (ctrl *AuthController) ChangePassword(c *gin.Context) {
	var req struct {
		CurrentPassword string `json:"current_password" binding:"required"`
		NewPassword     string `json:"new_password" binding:"required,min=6"`
	}
	
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error":   "Invalid request format",
			"details": err.Error(),
		})
		return
	}
	
	userID := middleware.GetUserID(c)
	if userID == 0 {
		c.JSON(http.StatusUnauthorized, gin.H{
			"error": "Authentication required",
		})
		return
	}
	
	db := database.GetDB()
	var user models.User
	
	if err := db.First(&user, userID).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{
			"error": "User not found",
		})
		return
	}
	
	// 验证当前密码
	if !user.CheckPassword(req.CurrentPassword) {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "Current password is incorrect",
		})
		return
	}
	
	// 更新密码
	user.Password = req.NewPassword
	if err := db.Save(&user).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "Failed to update password",
		})
		return
	}
	
	// 清除用户缓存
	cache := database.NewCache()
	cache.Delete(c, database.Keys.User(userID))
	
	c.JSON(http.StatusOK, gin.H{
		"status": 1,
		"msg":    "密码修改成功",
	})
}

// extractTokenFromHeader 从请求头中提取token
func extractTokenFromHeader(c *gin.Context) string {
	bearerToken := c.GetHeader("Authorization")
	if bearerToken != "" && strings.HasPrefix(bearerToken, "Bearer ") {
		return strings.TrimPrefix(bearerToken, "Bearer ")
	}
	return ""
}