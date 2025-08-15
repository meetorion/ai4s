package middleware

import (
	"net/http"
	"strings"
	"time"
	
	"github.com/gin-gonic/gin"
	"github.com/golang-jwt/jwt/v5"
	"iot-platform-backend/internal/config"
)

// Claims JWT声明结构
type Claims struct {
	UserID   uint   `json:"user_id"`
	Username string `json:"username"`
	Role     string `json:"role"`
	jwt.RegisteredClaims
}

// GenerateToken 生成JWT token
func GenerateToken(userID uint, username, role string) (string, error) {
	claims := Claims{
		UserID:   userID,
		Username: username,
		Role:     role,
		RegisteredClaims: jwt.RegisteredClaims{
			Issuer:    config.AppConfig.JWT.Issuer,
			ExpiresAt: jwt.NewNumericDate(time.Now().Add(config.AppConfig.JWT.Expires)),
			IssuedAt:  jwt.NewNumericDate(time.Now()),
			NotBefore: jwt.NewNumericDate(time.Now()),
		},
	}
	
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	return token.SignedString([]byte(config.AppConfig.JWT.Secret))
}

// GenerateRefreshToken 生成刷新token
func GenerateRefreshToken(userID uint) (string, error) {
	claims := jwt.RegisteredClaims{
		Issuer:    config.AppConfig.JWT.Issuer,
		Subject:   string(rune(userID)),
		ExpiresAt: jwt.NewNumericDate(time.Now().Add(config.AppConfig.JWT.RefreshExpires)),
		IssuedAt:  jwt.NewNumericDate(time.Now()),
		NotBefore: jwt.NewNumericDate(time.Now()),
	}
	
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	return token.SignedString([]byte(config.AppConfig.JWT.Secret))
}

// ParseToken 解析JWT token
func ParseToken(tokenString string) (*Claims, error) {
	token, err := jwt.ParseWithClaims(tokenString, &Claims{}, func(token *jwt.Token) (interface{}, error) {
		return []byte(config.AppConfig.JWT.Secret), nil
	})
	
	if err != nil {
		return nil, err
	}
	
	if claims, ok := token.Claims.(*Claims); ok && token.Valid {
		return claims, nil
	}
	
	return nil, jwt.ErrTokenInvalid
}

// AuthRequired JWT认证中间件
func AuthRequired() gin.HandlerFunc {
	return func(c *gin.Context) {
		token := extractToken(c)
		if token == "" {
			c.JSON(http.StatusUnauthorized, gin.H{
				"error": "Missing authorization token",
			})
			c.Abort()
			return
		}
		
		claims, err := ParseToken(token)
		if err != nil {
			c.JSON(http.StatusUnauthorized, gin.H{
				"error": "Invalid token: " + err.Error(),
			})
			c.Abort()
			return
		}
		
		// 将用户信息存储到上下文
		c.Set("user_id", claims.UserID)
		c.Set("username", claims.Username)
		c.Set("role", claims.Role)
		c.Set("claims", claims)
		
		c.Next()
	}
}

// OptionalAuth 可选认证中间件（用于支持匿名访问的接口）
func OptionalAuth() gin.HandlerFunc {
	return func(c *gin.Context) {
		token := extractToken(c)
		if token != "" {
			claims, err := ParseToken(token)
			if err == nil {
				c.Set("user_id", claims.UserID)
				c.Set("username", claims.Username)
				c.Set("role", claims.Role)
				c.Set("claims", claims)
			}
		}
		c.Next()
	}
}

// AdminRequired 管理员权限中间件
func AdminRequired() gin.HandlerFunc {
	return func(c *gin.Context) {
		role, exists := c.Get("role")
		if !exists {
			c.JSON(http.StatusUnauthorized, gin.H{
				"error": "Authentication required",
			})
			c.Abort()
			return
		}
		
		if role != "admin" {
			c.JSON(http.StatusForbidden, gin.H{
				"error": "Admin access required",
			})
			c.Abort()
			return
		}
		
		c.Next()
	}
}

// OwnerOrAdminRequired 资源拥有者或管理员权限中间件
func OwnerOrAdminRequired(ownerIDKey string) gin.HandlerFunc {
	return func(c *gin.Context) {
		currentUserID, exists := c.Get("user_id")
		if !exists {
			c.JSON(http.StatusUnauthorized, gin.H{
				"error": "Authentication required",
			})
			c.Abort()
			return
		}
		
		currentRole, _ := c.Get("role")
		
		// 管理员有所有权限
		if currentRole == "admin" {
			c.Next()
			return
		}
		
		// 检查是否为资源拥有者
		ownerID, exists := c.Get(ownerIDKey)
		if !exists {
			c.JSON(http.StatusForbidden, gin.H{
				"error": "Access denied: owner information not found",
			})
			c.Abort()
			return
		}
		
		if currentUserID != ownerID {
			c.JSON(http.StatusForbidden, gin.H{
				"error": "Access denied: you can only access your own resources",
			})
			c.Abort()
			return
		}
		
		c.Next()
	}
}

// RateLimitByUser 按用户限流中间件
func RateLimitByUser(maxRequests int, window time.Duration) gin.HandlerFunc {
	// 这里可以实现Redis-based的限流逻辑
	return func(c *gin.Context) {
		// TODO: 实现基于Redis的限流
		c.Next()
	}
}

// extractToken 从请求中提取token
func extractToken(c *gin.Context) string {
	// 从Authorization header中提取
	bearerToken := c.GetHeader("Authorization")
	if bearerToken != "" && strings.HasPrefix(bearerToken, "Bearer ") {
		return strings.TrimPrefix(bearerToken, "Bearer ")
	}
	
	// 从查询参数中提取（用于WebSocket等场景）
	token := c.Query("token")
	if token != "" {
		return token
	}
	
	// 从Cookie中提取
	cookie, err := c.Cookie("access_token")
	if err == nil && cookie != "" {
		return cookie
	}
	
	return ""
}

// GetCurrentUser 获取当前用户信息
func GetCurrentUser(c *gin.Context) (uint, string, string, bool) {
	userID, userExists := c.Get("user_id")
	username, nameExists := c.Get("username")
	role, roleExists := c.Get("role")
	
	if userExists && nameExists && roleExists {
		return userID.(uint), username.(string), role.(string), true
	}
	
	return 0, "", "", false
}

// IsAdmin 检查当前用户是否为管理员
func IsAdmin(c *gin.Context) bool {
	role, exists := c.Get("role")
	return exists && role == "admin"
}

// GetUserID 获取当前用户ID
func GetUserID(c *gin.Context) uint {
	if userID, exists := c.Get("user_id"); exists {
		return userID.(uint)
	}
	return 0
}