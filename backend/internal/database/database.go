package database

import (
	"fmt"
	"log"
	"os"
	"time"
	
	"iot-platform-backend/internal/models"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
	"gorm.io/gorm/logger"
)

var DB *gorm.DB

// Config 数据库配置
type Config struct {
	Host     string
	Port     string
	User     string
	Password string
	DBName   string
	SSLMode  string
	TimeZone string
}

// Connect 连接数据库
func Connect(cfg *Config) error {
	dsn := fmt.Sprintf(
		"host=%s port=%s user=%s password=%s dbname=%s sslmode=%s TimeZone=%s",
		cfg.Host, cfg.Port, cfg.User, cfg.Password, cfg.DBName, cfg.SSLMode, cfg.TimeZone,
	)
	
	// 配置GORM日志
	var gormLogger logger.Interface
	if os.Getenv("GIN_MODE") == "debug" {
		gormLogger = logger.Default.LogMode(logger.Info)
	} else {
		gormLogger = logger.Default.LogMode(logger.Error)
	}
	
	// 连接数据库
	db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{
		Logger: gormLogger,
		NowFunc: func() time.Time {
			return time.Now().UTC()
		},
	})
	
	if err != nil {
		return fmt.Errorf("failed to connect to database: %w", err)
	}
	
	// 配置连接池
	sqlDB, err := db.DB()
	if err != nil {
		return fmt.Errorf("failed to get database connection: %w", err)
	}
	
	// 设置连接池参数
	sqlDB.SetMaxOpenConns(25)                // 最大打开连接数
	sqlDB.SetMaxIdleConns(5)                 // 最大空闲连接数
	sqlDB.SetConnMaxLifetime(time.Hour)      // 连接最大生命周期
	sqlDB.SetConnMaxIdleTime(10 * time.Minute) // 连接最大空闲时间
	
	DB = db
	log.Println("Database connected successfully")
	return nil
}

// Migrate 自动迁移数据库表
func Migrate() error {
	if DB == nil {
		return fmt.Errorf("database connection not initialized")
	}
	
	// 自动迁移所有模型
	err := DB.AutoMigrate(
		&models.User{},
		&models.Device{},
		&models.SensorData{},
		&models.Project{},
		&models.Fork{},
		&models.ForkHistory{},
		&models.ProjectStar{},
		&models.PullRequest{},
		&models.ProjectTemplate{},
	)
	
	if err != nil {
		return fmt.Errorf("failed to migrate database: %w", err)
	}
	
	// 创建自定义索引
	if err := createIndexes(); err != nil {
		return fmt.Errorf("failed to create indexes: %w", err)
	}
	
	log.Println("Database migration completed successfully")
	return nil
}

// createIndexes 创建自定义索引
func createIndexes() error {
	// 创建复合索引
	indexes := []string{
		"CREATE INDEX IF NOT EXISTS idx_sensor_data_device_time ON sensor_data(device_id, timestamp DESC)",
		"CREATE INDEX IF NOT EXISTS idx_devices_owner_type ON devices(owner_id, type)",
		"CREATE INDEX IF NOT EXISTS idx_projects_owner_public ON projects(owner_id, public)",
		"CREATE UNIQUE INDEX IF NOT EXISTS idx_forks_user_project ON forks(user_id, project_id)",
		"CREATE UNIQUE INDEX IF NOT EXISTS idx_project_stars_user_project ON project_stars(user_id, project_id)",
		"CREATE INDEX IF NOT EXISTS idx_fork_history_project_time ON fork_history(project_id, created_at DESC)",
	}
	
	for _, index := range indexes {
		if err := DB.Exec(index).Error; err != nil {
			return fmt.Errorf("failed to create index: %s, error: %w", index, err)
		}
	}
	
	return nil
}

// Close 关闭数据库连接
func Close() error {
	if DB == nil {
		return nil
	}
	
	sqlDB, err := DB.DB()
	if err != nil {
		return err
	}
	
	return sqlDB.Close()
}

// GetDB 获取数据库实例
func GetDB() *gorm.DB {
	return DB
}

// Transaction 执行事务
func Transaction(fn func(*gorm.DB) error) error {
	return DB.Transaction(fn)
}

// Health 健康检查
func Health() error {
	if DB == nil {
		return fmt.Errorf("database connection not initialized")
	}
	
	sqlDB, err := DB.DB()
	if err != nil {
		return err
	}
	
	return sqlDB.Ping()
}

// Stats 获取数据库统计信息
func Stats() (map[string]interface{}, error) {
	if DB == nil {
		return nil, fmt.Errorf("database connection not initialized")
	}
	
	sqlDB, err := DB.DB()
	if err != nil {
		return nil, err
	}
	
	stats := sqlDB.Stats()
	
	return map[string]interface{}{
		"open_connections":     stats.OpenConnections,
		"in_use":              stats.InUse,
		"idle":                stats.Idle,
		"wait_count":          stats.WaitCount,
		"wait_duration":       stats.WaitDuration.String(),
		"max_idle_closed":     stats.MaxIdleClosed,
		"max_idle_time_closed": stats.MaxIdleTimeClosed,
		"max_lifetime_closed": stats.MaxLifetimeClosed,
	}, nil
}