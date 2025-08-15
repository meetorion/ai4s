package config

import (
	"fmt"
	"os"
	"strconv"
	"time"
	
	"github.com/joho/godotenv"
)

// Config 应用配置结构
type Config struct {
	Server   ServerConfig   `json:"server"`
	Database DatabaseConfig `json:"database"`
	Redis    RedisConfig    `json:"redis"`
	JWT      JWTConfig      `json:"jwt"`
	WebSocket WebSocketConfig `json:"websocket"`
	Log      LogConfig      `json:"log"`
}

// ServerConfig 服务器配置
type ServerConfig struct {
	Port         string        `json:"port"`
	Mode         string        `json:"mode"`         // debug, release
	ReadTimeout  time.Duration `json:"read_timeout"`
	WriteTimeout time.Duration `json:"write_timeout"`
	CORS         CORSConfig    `json:"cors"`
}

// DatabaseConfig 数据库配置
type DatabaseConfig struct {
	Host     string `json:"host"`
	Port     string `json:"port"`
	User     string `json:"user"`
	Password string `json:"password"`
	DBName   string `json:"db_name"`
	SSLMode  string `json:"ssl_mode"`
	TimeZone string `json:"time_zone"`
}

// RedisConfig Redis配置
type RedisConfig struct {
	Host     string `json:"host"`
	Port     string `json:"port"`
	Password string `json:"password"`
	DB       int    `json:"db"`
}

// JWTConfig JWT配置
type JWTConfig struct {
	Secret     string        `json:"secret"`
	Expires    time.Duration `json:"expires"`
	RefreshExpires time.Duration `json:"refresh_expires"`
	Issuer     string        `json:"issuer"`
}

// WebSocketConfig WebSocket配置
type WebSocketConfig struct {
	ReadBufferSize  int           `json:"read_buffer_size"`
	WriteBufferSize int           `json:"write_buffer_size"`
	CheckOrigin     bool          `json:"check_origin"`
	HandshakeTimeout time.Duration `json:"handshake_timeout"`
	MaxMessageSize   int64         `json:"max_message_size"`
}

// CORSConfig CORS配置
type CORSConfig struct {
	AllowedOrigins     []string `json:"allowed_origins"`
	AllowedMethods     []string `json:"allowed_methods"`
	AllowedHeaders     []string `json:"allowed_headers"`
	ExposedHeaders     []string `json:"exposed_headers"`
	AllowCredentials   bool     `json:"allow_credentials"`
	MaxAge            time.Duration `json:"max_age"`
}

// LogConfig 日志配置
type LogConfig struct {
	Level      string `json:"level"`    // debug, info, warn, error
	Format     string `json:"format"`   // json, text
	Output     string `json:"output"`   // stdout, file
	FilePath   string `json:"file_path"`
	MaxSize    int    `json:"max_size"`    // MB
	MaxBackups int    `json:"max_backups"`
	MaxAge     int    `json:"max_age"`     // days
	Compress   bool   `json:"compress"`
}

var AppConfig *Config

// Load 加载配置
func Load() (*Config, error) {
	// 尝试加载.env文件
	if err := godotenv.Load(); err != nil {
		fmt.Println("Warning: .env file not found, using environment variables")
	}
	
	config := &Config{
		Server: ServerConfig{
			Port:         getEnvWithDefault("PORT", "8080"),
			Mode:         getEnvWithDefault("GIN_MODE", "debug"),
			ReadTimeout:  getDurationEnvWithDefault("READ_TIMEOUT", 30*time.Second),
			WriteTimeout: getDurationEnvWithDefault("WRITE_TIMEOUT", 30*time.Second),
			CORS: CORSConfig{
				AllowedOrigins: []string{
					getEnvWithDefault("FRONTEND_URL", "http://localhost:8501"),
					"http://localhost:3000", // React开发服务器
					"http://127.0.0.1:8501", // Streamlit默认地址
				},
				AllowedMethods: []string{"GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"},
				AllowedHeaders: []string{
					"Origin", "Content-Type", "Accept", "Authorization",
					"X-Requested-With", "X-CSRF-Token",
				},
				ExposedHeaders:   []string{"X-Total-Count"},
				AllowCredentials: true,
				MaxAge:          12 * time.Hour,
			},
		},
		Database: DatabaseConfig{
			Host:     getEnvWithDefault("DB_HOST", "localhost"),
			Port:     getEnvWithDefault("DB_PORT", "5432"),
			User:     getEnvWithDefault("DB_USER", "postgres"),
			Password: getEnvWithDefault("DB_PASSWORD", "password"),
			DBName:   getEnvWithDefault("DB_NAME", "iot_platform"),
			SSLMode:  getEnvWithDefault("DB_SSL_MODE", "disable"),
			TimeZone: getEnvWithDefault("DB_TIMEZONE", "UTC"),
		},
		Redis: RedisConfig{
			Host:     getEnvWithDefault("REDIS_HOST", "localhost"),
			Port:     getEnvWithDefault("REDIS_PORT", "6379"),
			Password: getEnvWithDefault("REDIS_PASSWORD", ""),
			DB:       getIntEnvWithDefault("REDIS_DB", 0),
		},
		JWT: JWTConfig{
			Secret:         getEnvWithDefault("JWT_SECRET", "your-secret-key-change-in-production"),
			Expires:        getDurationEnvWithDefault("JWT_EXPIRES", 24*time.Hour),
			RefreshExpires: getDurationEnvWithDefault("JWT_REFRESH_EXPIRES", 7*24*time.Hour),
			Issuer:         getEnvWithDefault("JWT_ISSUER", "iot-platform"),
		},
		WebSocket: WebSocketConfig{
			ReadBufferSize:   getIntEnvWithDefault("WS_READ_BUFFER", 1024),
			WriteBufferSize:  getIntEnvWithDefault("WS_WRITE_BUFFER", 1024),
			CheckOrigin:      getBoolEnvWithDefault("WS_CHECK_ORIGIN", false),
			HandshakeTimeout: getDurationEnvWithDefault("WS_HANDSHAKE_TIMEOUT", 10*time.Second),
			MaxMessageSize:   getInt64EnvWithDefault("WS_MAX_MESSAGE_SIZE", 512),
		},
		Log: LogConfig{
			Level:      getEnvWithDefault("LOG_LEVEL", "info"),
			Format:     getEnvWithDefault("LOG_FORMAT", "json"),
			Output:     getEnvWithDefault("LOG_OUTPUT", "stdout"),
			FilePath:   getEnvWithDefault("LOG_FILE_PATH", "./logs/app.log"),
			MaxSize:    getIntEnvWithDefault("LOG_MAX_SIZE", 100),
			MaxBackups: getIntEnvWithDefault("LOG_MAX_BACKUPS", 3),
			MaxAge:     getIntEnvWithDefault("LOG_MAX_AGE", 28),
			Compress:   getBoolEnvWithDefault("LOG_COMPRESS", true),
		},
	}
	
	AppConfig = config
	return config, nil
}

// Validate 验证配置
func (c *Config) Validate() error {
	if c.JWT.Secret == "your-secret-key-change-in-production" {
		return fmt.Errorf("please change JWT secret in production")
	}
	
	if c.Database.Password == "" {
		return fmt.Errorf("database password is required")
	}
	
	return nil
}

// IsDevelopment 是否为开发环境
func (c *Config) IsDevelopment() bool {
	return c.Server.Mode == "debug"
}

// IsProduction 是否为生产环境
func (c *Config) IsProduction() bool {
	return c.Server.Mode == "release"
}

// 辅助函数
func getEnvWithDefault(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

func getIntEnvWithDefault(key string, defaultValue int) int {
	if value := os.Getenv(key); value != "" {
		if intValue, err := strconv.Atoi(value); err == nil {
			return intValue
		}
	}
	return defaultValue
}

func getInt64EnvWithDefault(key string, defaultValue int64) int64 {
	if value := os.Getenv(key); value != "" {
		if intValue, err := strconv.ParseInt(value, 10, 64); err == nil {
			return intValue
		}
	}
	return defaultValue
}

func getBoolEnvWithDefault(key string, defaultValue bool) bool {
	if value := os.Getenv(key); value != "" {
		if boolValue, err := strconv.ParseBool(value); err == nil {
			return boolValue
		}
	}
	return defaultValue
}

func getDurationEnvWithDefault(key string, defaultValue time.Duration) time.Duration {
	if value := os.Getenv(key); value != "" {
		if duration, err := time.ParseDuration(value); err == nil {
			return duration
		}
	}
	return defaultValue
}