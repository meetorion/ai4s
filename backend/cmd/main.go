package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"
	
	"github.com/gin-gonic/gin"
	"iot-platform-backend/internal/api"
	"iot-platform-backend/internal/config"
	"iot-platform-backend/internal/database"
	"iot-platform-backend/internal/websocket"
)

func main() {
	// 加载配置
	cfg, err := config.Load()
	if err != nil {
		log.Fatalf("Failed to load config: %v", err)
	}
	
	// 验证配置
	if err := cfg.Validate(); err != nil {
		log.Fatalf("Config validation failed: %v", err)
	}
	
	// 设置Gin模式
	gin.SetMode(cfg.Server.Mode)
	
	// 连接数据库
	dbConfig := &database.Config{
		Host:     cfg.Database.Host,
		Port:     cfg.Database.Port,
		User:     cfg.Database.User,
		Password: cfg.Database.Password,
		DBName:   cfg.Database.DBName,
		SSLMode:  cfg.Database.SSLMode,
		TimeZone: cfg.Database.TimeZone,
	}
	
	if err := database.Connect(dbConfig); err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}
	
	// 自动迁移数据库
	if err := database.Migrate(); err != nil {
		log.Fatalf("Database migration failed: %v", err)
	}
	
	// 连接Redis
	redisConfig := &database.RedisConfig{
		Host:     cfg.Redis.Host,
		Port:     cfg.Redis.Port,
		Password: cfg.Redis.Password,
		DB:       cfg.Redis.DB,
	}
	
	if err := database.ConnectRedis(redisConfig); err != nil {
		log.Fatalf("Failed to connect to Redis: %v", err)
	}
	
	// 初始化WebSocket管理器
	websocket.Init()
	
	// 创建Gin引擎
	r := gin.New()
	
	// 设置路由
	api.SetupRoutes(r)
	
	// 创建HTTP服务器
	srv := &http.Server{
		Addr:         ":" + cfg.Server.Port,
		Handler:      r,
		ReadTimeout:  cfg.Server.ReadTimeout,
		WriteTimeout: cfg.Server.WriteTimeout,
	}
	
	// 在goroutine中启动服务器
	go func() {
		log.Printf("Server starting on port %s", cfg.Server.Port)
		log.Printf("Health check available at: http://localhost:%s/health", cfg.Server.Port)
		log.Printf("API documentation available at: http://localhost:%s/api/v1", cfg.Server.Port)
		
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("Server failed to start: %v", err)
		}
	}()
	
	// 等待中断信号以优雅关闭服务器
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit
	
	log.Println("Shutting down server...")
	
	// 创建一个超时上下文，给服务器30秒时间完成现有请求
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()
	
	// 优雅关闭服务器
	if err := srv.Shutdown(ctx); err != nil {
		log.Printf("Server forced to shutdown: %v", err)
	}
	
	// 关闭数据库连接
	if err := database.Close(); err != nil {
		log.Printf("Failed to close database connection: %v", err)
	}
	
	// 关闭Redis连接
	if err := database.CloseRedis(); err != nil {
		log.Printf("Failed to close Redis connection: %v", err)
	}
	
	log.Println("Server exited")
}