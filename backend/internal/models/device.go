package models

import (
	"time"
	"database/sql/driver"
	"encoding/json"
	"fmt"
)

// DeviceType 设备类型枚举
type DeviceType int

const (
	WeatherStation DeviceType = iota + 1 // 气象站
	SoilMoisture                         // 土壤墒情
	WaterQuality                         // 水质监测
	VideoMonitor                         // 视频监控
	PowerCabinet                         // 配电柜
	PestMonitor                          // 虫情监测
	SporeDetector                        // 孢子仪
	EnvMonitor                           // 环境监测
	SmartIrrigation                      // 智能灌溉
	InsectKiller                         // 杀虫灯
	SluiceGate                           // 一体化闸门
	WaterSensor                          // 积水传感器
	PlantGrowth                          // 植物生长记录仪
)

var DeviceTypeNames = map[DeviceType]string{
	WeatherStation:  "气象站",
	SoilMoisture:    "土壤墒情",
	WaterQuality:    "水质监测",
	VideoMonitor:    "视频监控",
	PowerCabinet:    "配电柜",
	PestMonitor:     "虫情监测",
	SporeDetector:   "孢子仪",
	EnvMonitor:      "环境监测",
	SmartIrrigation: "智能灌溉",
	InsectKiller:    "杀虫灯",
	SluiceGate:      "一体化闸门",
	WaterSensor:     "积水传感器",
	PlantGrowth:     "植物生长记录仪",
}

// JSONB 自定义类型用于存储JSON数据
type JSONB map[string]interface{}

// Value 实现driver.Valuer接口
func (j JSONB) Value() (driver.Value, error) {
	return json.Marshal(j)
}

// Scan 实现sql.Scanner接口
func (j *JSONB) Scan(value interface{}) error {
	if value == nil {
		*j = make(map[string]interface{})
		return nil
	}
	
	switch v := value.(type) {
	case []byte:
		return json.Unmarshal(v, j)
	case string:
		return json.Unmarshal([]byte(v), j)
	default:
		return fmt.Errorf("cannot scan %T into JSONB", value)
	}
}

// Device 设备模型
type Device struct {
	ID         uint       `json:"id" gorm:"primarykey"`
	DeviceID   string     `json:"device_id" gorm:"unique;not null;index"` // 设备唯一标识
	Name       string     `json:"name" gorm:"not null"`
	Type       DeviceType `json:"type" gorm:"not null;index"`
	TypeName   string     `json:"type_name" gorm:"-"` // 不存储在数据库中
	Location   JSONB      `json:"location" gorm:"type:jsonb"` // 地理位置信息
	Config     JSONB      `json:"config" gorm:"type:jsonb"`   // 设备配置
	Status     string     `json:"status" gorm:"default:offline"` // online, offline, error
	LastSeen   *time.Time `json:"last_seen"`
	OwnerID    uint       `json:"owner_id" gorm:"index"`
	CreatedAt  time.Time  `json:"created_at"`
	UpdatedAt  time.Time  `json:"updated_at"`
	
	// 关联关系
	Owner       User         `json:"owner,omitempty" gorm:"foreignKey:OwnerID"`
	SensorData  []SensorData `json:"sensor_data,omitempty" gorm:"foreignKey:DeviceID;references:DeviceID"`
}

// TableName 指定表名
func (Device) TableName() string {
	return "devices"
}

// AfterFind GORM钩子：查询后设置类型名称
func (d *Device) AfterFind(tx *gorm.DB) error {
	if name, exists := DeviceTypeNames[d.Type]; exists {
		d.TypeName = name
	}
	return nil
}

// IsOnline 检查设备是否在线
func (d *Device) IsOnline() bool {
	if d.LastSeen == nil {
		return false
	}
	// 如果5分钟内有数据则认为在线
	return time.Since(*d.LastSeen) < 5*time.Minute
}

// SensorData 传感器数据模型
type SensorData struct {
	ID        uint      `json:"id" gorm:"primarykey"`
	DeviceID  string    `json:"device_id" gorm:"not null;index"`
	Data      JSONB     `json:"data" gorm:"type:jsonb"` // 传感器数据JSON
	Timestamp time.Time `json:"timestamp" gorm:"index"`
	CreatedAt time.Time `json:"created_at"`
	
	// 关联关系
	Device Device `json:"device,omitempty" gorm:"foreignKey:DeviceID;references:DeviceID"`
}

// TableName 指定表名
func (SensorData) TableName() string {
	return "sensor_data"
}

// DeviceStatus 设备状态统计
type DeviceStatus struct {
	Type       DeviceType `json:"type"`
	TypeName   string     `json:"type_name"`
	Total      int64      `json:"total"`
	Online     int64      `json:"online"`
	Offline    int64      `json:"offline"`
	LastUpdate time.Time  `json:"last_update"`
}