package middleware

import (
	"fmt"
	"io"
	"os"
	"time"
	
	"github.com/gin-gonic/gin"
	"github.com/sirupsen/logrus"
	"iot-platform-backend/internal/config"
)

// Logger 日志中间件
func Logger() gin.HandlerFunc {
	// 配置logrus
	logger := logrus.New()
	
	// 设置日志级别
	level, err := logrus.ParseLevel(config.AppConfig.Log.Level)
	if err != nil {
		level = logrus.InfoLevel
	}
	logger.SetLevel(level)
	
	// 设置日志格式
	if config.AppConfig.Log.Format == "json" {
		logger.SetFormatter(&logrus.JSONFormatter{
			TimestampFormat: time.RFC3339,
		})
	} else {
		logger.SetFormatter(&logrus.TextFormatter{
			FullTimestamp:   true,
			TimestampFormat: time.RFC3339,
		})
	}
	
	// 设置输出
	if config.AppConfig.Log.Output == "file" {
		// 确保日志目录存在
		logDir := "logs"
		if _, err := os.Stat(logDir); os.IsNotExist(err) {
			os.MkdirAll(logDir, 0755)
		}
		
		file, err := os.OpenFile(config.AppConfig.Log.FilePath, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0666)
		if err != nil {
			logger.SetOutput(os.Stdout)
		} else {
			// 同时输出到文件和控制台
			logger.SetOutput(io.MultiWriter(os.Stdout, file))
		}
	} else {
		logger.SetOutput(os.Stdout)
	}
	
	return LoggerWithConfig(LoggerConfig{
		Logger: logger,
		SkipPaths: []string{
			"/health",
			"/metrics",
		},
	})
}

// LoggerConfig 日志中间件配置
type LoggerConfig struct {
	Logger     *logrus.Logger
	SkipPaths  []string
	TimeFormat string
}

// LoggerWithConfig 带配置的日志中间件
func LoggerWithConfig(config LoggerConfig) gin.HandlerFunc {
	logger := config.Logger
	if logger == nil {
		logger = logrus.New()
	}
	
	skipPaths := make(map[string]bool, len(config.SkipPaths))
	for _, path := range config.SkipPaths {
		skipPaths[path] = true
	}
	
	timeFormat := config.TimeFormat
	if timeFormat == "" {
		timeFormat = time.RFC3339
	}
	
	return gin.HandlerFunc(func(c *gin.Context) {
		// 跳过某些路径的日志记录
		if skipPaths[c.Request.URL.Path] {
			c.Next()
			return
		}
		
		start := time.Now()
		path := c.Request.URL.Path
		raw := c.Request.URL.RawQuery
		
		// 执行请求
		c.Next()
		
		// 计算延迟
		latency := time.Since(start)
		
		// 构建日志字段
		fields := logrus.Fields{
			"status":     c.Writer.Status(),
			"method":     c.Request.Method,
			"path":       path,
			"ip":         c.ClientIP(),
			"latency":    latency,
			"user_agent": c.Request.UserAgent(),
		}
		
		// 添加查询参数
		if raw != "" {
			fields["query"] = raw
		}
		
		// 添加用户信息（如果已认证）
		if userID, exists := c.Get("user_id"); exists {
			fields["user_id"] = userID
		}
		
		if username, exists := c.Get("username"); exists {
			fields["username"] = username
		}
		
		// 添加请求ID（如果存在）
		if requestID := c.GetHeader("X-Request-ID"); requestID != "" {
			fields["request_id"] = requestID
		}
		
		// 添加错误信息（如果有）
		if len(c.Errors) > 0 {
			fields["errors"] = c.Errors.String()
		}
		
		// 根据状态码选择日志级别
		status := c.Writer.Status()
		msg := fmt.Sprintf("%s %s", c.Request.Method, path)
		
		switch {
		case status >= 500:
			logger.WithFields(fields).Error(msg)
		case status >= 400:
			logger.WithFields(fields).Warn(msg)
		default:
			logger.WithFields(fields).Info(msg)
		}
	})
}

// RequestID 请求ID中间件
func RequestID() gin.HandlerFunc {
	return func(c *gin.Context) {
		requestID := c.GetHeader("X-Request-ID")
		if requestID == "" {
			requestID = generateRequestID()
		}
		
		c.Header("X-Request-ID", requestID)
		c.Set("request_id", requestID)
		c.Next()
	}
}

// generateRequestID 生成请求ID
func generateRequestID() string {
	return fmt.Sprintf("%d-%s", time.Now().UnixNano(), generateRandomString(8))
}