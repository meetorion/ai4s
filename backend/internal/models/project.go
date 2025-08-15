package models

import (
	"time"
	"github.com/lib/pq"
)

// Project 项目配置模型
type Project struct {
	ID          uint           `json:"id" gorm:"primarykey"`
	Name        string         `json:"name" gorm:"not null"`
	Description string         `json:"description"`
	OwnerID     uint           `json:"owner_id" gorm:"not null;index"`
	ParentID    *uint          `json:"parent_id" gorm:"index"` // Fork来源项目ID
	Config      JSONB          `json:"config" gorm:"type:jsonb"` // 项目配置JSON
	Public      bool           `json:"public" gorm:"default:false"`
	Tags        pq.StringArray `json:"tags" gorm:"type:text[]"` // 项目标签
	StarCount   int            `json:"star_count" gorm:"default:0"`
	ForkCount   int            `json:"fork_count" gorm:"default:0"`
	ViewCount   int            `json:"view_count" gorm:"default:0"`
	CreatedAt   time.Time      `json:"created_at"`
	UpdatedAt   time.Time      `json:"updated_at"`
	
	// 关联关系
	Owner    User      `json:"owner,omitempty" gorm:"foreignKey:OwnerID"`
	Parent   *Project  `json:"parent,omitempty" gorm:"foreignKey:ParentID"`
	Children []Project `json:"children,omitempty" gorm:"foreignKey:ParentID"`
	Stars    []ProjectStar `json:"stars,omitempty" gorm:"foreignKey:ProjectID"`
	Forks    []Fork    `json:"forks,omitempty" gorm:"foreignKey:ProjectID"`
	History  []ForkHistory `json:"history,omitempty" gorm:"foreignKey:ProjectID"`
}

// TableName 指定表名
func (Project) TableName() string {
	return "projects"
}

// IsForked 检查是否为Fork项目
func (p *Project) IsForked() bool {
	return p.ParentID != nil
}

// IncrementForkCount 增加Fork数量
func (p *Project) IncrementForkCount() {
	p.ForkCount++
}

// IncrementStarCount 增加Star数量
func (p *Project) IncrementStarCount() {
	p.StarCount++
}

// IncrementViewCount 增加查看数量
func (p *Project) IncrementViewCount() {
	p.ViewCount++
}

// Fork Fork记录模型
type Fork struct {
	ID        uint      `json:"id" gorm:"primarykey"`
	ProjectID uint      `json:"project_id" gorm:"not null;index"`
	UserID    uint      `json:"user_id" gorm:"not null;index"`
	Config    JSONB     `json:"config" gorm:"type:jsonb"` // Fork时的配置快照
	Message   string    `json:"message"` // Fork说明
	CreatedAt time.Time `json:"created_at"`
	
	// 关联关系
	Project Project `json:"project,omitempty" gorm:"foreignKey:ProjectID"`
	User    User    `json:"user,omitempty" gorm:"foreignKey:UserID"`
	
	// 联合唯一索引
	// gorm:"uniqueIndex:idx_user_project"
}

// TableName 指定表名
func (Fork) TableName() string {
	return "forks"
}

// ForkHistory Fork历史记录模型
type ForkHistory struct {
	ID         uint      `json:"id" gorm:"primarykey"`
	ProjectID  uint      `json:"project_id" gorm:"not null;index"`
	UserID     uint      `json:"user_id" gorm:"not null;index"`
	Action     string    `json:"action" gorm:"not null"` // create, update, merge, revert
	ConfigDiff JSONB     `json:"config_diff" gorm:"type:jsonb"` // 配置差异
	Message    string    `json:"message"` // 操作说明
	IPAddress  string    `json:"ip_address"`
	UserAgent  string    `json:"user_agent"`
	CreatedAt  time.Time `json:"created_at"`
	
	// 关联关系
	Project Project `json:"project,omitempty" gorm:"foreignKey:ProjectID"`
	User    User    `json:"user,omitempty" gorm:"foreignKey:UserID"`
}

// TableName 指定表名
func (ForkHistory) TableName() string {
	return "fork_history"
}

// ProjectStar 项目点赞模型
type ProjectStar struct {
	ID        uint      `json:"id" gorm:"primarykey"`
	ProjectID uint      `json:"project_id" gorm:"not null;index"`
	UserID    uint      `json:"user_id" gorm:"not null;index"`
	CreatedAt time.Time `json:"created_at"`
	
	// 关联关系
	Project Project `json:"project,omitempty" gorm:"foreignKey:ProjectID"`
	User    User    `json:"user,omitempty" gorm:"foreignKey:UserID"`
	
	// 联合唯一索引：每个用户只能给同一个项目点一次赞
	// gorm:"uniqueIndex:idx_user_project_star"
}

// TableName 指定表名
func (ProjectStar) TableName() string {
	return "project_stars"
}

// PullRequest 合并请求模型（可选功能）
type PullRequest struct {
	ID          uint      `json:"id" gorm:"primarykey"`
	Title       string    `json:"title" gorm:"not null"`
	Description string    `json:"description"`
	SourceID    uint      `json:"source_id" gorm:"not null"` // 源项目ID
	TargetID    uint      `json:"target_id" gorm:"not null"` // 目标项目ID
	UserID      uint      `json:"user_id" gorm:"not null"`   // 提交用户ID
	Status      string    `json:"status" gorm:"default:open"` // open, merged, closed
	ConfigDiff  JSONB     `json:"config_diff" gorm:"type:jsonb"` // 配置差异
	CreatedAt   time.Time `json:"created_at"`
	UpdatedAt   time.Time `json:"updated_at"`
	
	// 关联关系
	Source Project `json:"source,omitempty" gorm:"foreignKey:SourceID"`
	Target Project `json:"target,omitempty" gorm:"foreignKey:TargetID"`
	User   User    `json:"user,omitempty" gorm:"foreignKey:UserID"`
}

// TableName 指定表名
func (PullRequest) TableName() string {
	return "pull_requests"
}

// ProjectTemplate 项目模板模型
type ProjectTemplate struct {
	ID          uint           `json:"id" gorm:"primarykey"`
	Name        string         `json:"name" gorm:"not null"`
	Description string         `json:"description"`
	Category    string         `json:"category"` // dashboard, analysis, monitoring
	Config      JSONB          `json:"config" gorm:"type:jsonb"`
	Tags        pq.StringArray `json:"tags" gorm:"type:text[]"`
	UseCount    int            `json:"use_count" gorm:"default:0"`
	Featured    bool           `json:"featured" gorm:"default:false"`
	CreatedBy   uint           `json:"created_by"`
	CreatedAt   time.Time      `json:"created_at"`
	UpdatedAt   time.Time      `json:"updated_at"`
	
	// 关联关系
	Creator User `json:"creator,omitempty" gorm:"foreignKey:CreatedBy"`
}

// TableName 指定表名
func (ProjectTemplate) TableName() string {
	return "project_templates"
}