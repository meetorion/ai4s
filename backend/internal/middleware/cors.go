package middleware

import (
	"time"
	
	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
	"iot-platform-backend/internal/config"
)

// CORS 跨域中间件
func CORS() gin.HandlerFunc {
	cfg := config.AppConfig.Server.CORS
	
	return cors.New(cors.Config{
		AllowOrigins:     cfg.AllowedOrigins,
		AllowMethods:     cfg.AllowedMethods,
		AllowHeaders:     cfg.AllowedHeaders,
		ExposeHeaders:    cfg.ExposedHeaders,
		AllowCredentials: cfg.AllowCredentials,
		MaxAge:          cfg.MaxAge,
		
		// 自定义Origin检查函数
		AllowOriginFunc: func(origin string) bool {
			// 开发环境允许localhost和127.0.0.1的任何端口
			if config.AppConfig.IsDevelopment() {
				return true
			}
			
			// 生产环境严格检查Origin
			for _, allowedOrigin := range cfg.AllowedOrigins {
				if origin == allowedOrigin {
					return true
				}
			}
			
			return false
		},
	})
}