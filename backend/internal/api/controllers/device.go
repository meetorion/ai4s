package controllers

import (
	"net/http"
	"strconv"
	"time"
	
	"github.com/gin-gonic/gin"
	"iot-platform-backend/internal/database"
	"iot-platform-backend/internal/middleware"
	"iot-platform-backend/internal/models"
	"iot-platform-backend/internal/websocket"
)

// DeviceController 设备控制器
type DeviceController struct{}

// NewDeviceController 创建设备控制器
func NewDeviceController() *DeviceController {
	return &DeviceController{}
}

// CreateDeviceRequest 创建设备请求
type CreateDeviceRequest struct {
	DeviceID string                 `json:"device_id" binding:"required"`
	Name     string                 `json:"name" binding:"required"`
	Type     models.DeviceType      `json:"type" binding:"required,min=1,max=13"`
	Location models.JSONB           `json:"location"`
	Config   models.JSONB           `json:"config"`
}

// UpdateDeviceRequest 更新设备请求
type UpdateDeviceRequest struct {
	Name     string       `json:"name"`
	Location models.JSONB `json:"location"`
	Config   models.JSONB `json:"config"`
}

// DeviceListResponse 设备列表响应
type DeviceListResponse struct {
	Devices []models.Device `json:"devices"`
	Total   int64           `json:"total"`
	Page    int             `json:"page"`
	Limit   int             `json:"limit"`
}

// GetDevices 获取设备列表
// @Summary 获取设备列表
// @Description 获取用户的设备列表，支持分页和筛选
// @Tags 设备管理
// @Security BearerAuth
// @Produce json
// @Param page query int false "页码" default(1)
// @Param limit query int false "每页数量" default(10)
// @Param type query int false "设备类型筛选"
// @Param name query string false "设备名称筛选"
// @Param status query string false "设备状态筛选"
// @Success 200 {object} DeviceListResponse
// @Router /devices [get]
func (ctrl *DeviceController) GetDevices(c *gin.Context) {
	userID := middleware.GetUserID(c)
	if userID == 0 {
		c.JSON(http.StatusUnauthorized, gin.H{
			"error": "Authentication required",
		})
		return
	}
	
	// 解析分页参数
	page, _ := strconv.Atoi(c.DefaultQuery("page", "1"))
	limit, _ := strconv.Atoi(c.DefaultQuery("limit", "10"))
	if page < 1 {
		page = 1
	}
	if limit < 1 || limit > 100 {
		limit = 10
	}
	
	offset := (page - 1) * limit
	
	// 尝试从缓存获取
	cache := database.NewCache()
	cacheKey := database.Keys.DeviceList(userID)
	
	var devices []models.Device
	var total int64
	
	// 构建查询
	db := database.GetDB()
	query := db.Where("owner_id = ?", userID)
	
	// 应用筛选
	if deviceType := c.Query("type"); deviceType != "" {
		if typeInt, err := strconv.Atoi(deviceType); err == nil {
			query = query.Where("type = ?", typeInt)
		}
	}
	
	if name := c.Query("name"); name != "" {
		query = query.Where("name ILIKE ?", "%"+name+"%")
	}
	
	if status := c.Query("status"); status != "" {
		query = query.Where("status = ?", status)
	}
	
	// 获取总数
	query.Model(&models.Device{}).Count(&total)
	
	// 获取设备列表
	if err := query.Offset(offset).Limit(limit).Find(&devices).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "Failed to fetch devices",
		})
		return
	}
	
	// 更新设备状态（基于最后通信时间）
	for i := range devices {
		if devices[i].IsOnline() {
			devices[i].Status = "online"
		} else {
			devices[i].Status = "offline"
		}
	}
	
	response := DeviceListResponse{
		Devices: devices,
		Total:   total,
		Page:    page,
		Limit:   limit,
	}
	
	c.JSON(http.StatusOK, gin.H{
		"status": 1,
		"data":   response,
	})
}

// GetDevice 获取单个设备详情
// @Summary 获取设备详情
// @Description 根据ID获取设备的详细信息
// @Tags 设备管理
// @Security BearerAuth
// @Produce json
// @Param id path int true "设备ID"
// @Success 200 {object} models.Device
// @Failure 404 {object} map[string]interface{}
// @Router /devices/{id} [get]
func (ctrl *DeviceController) GetDevice(c *gin.Context) {
	userID := middleware.GetUserID(c)
	deviceID, err := strconv.ParseUint(c.Param("id"), 10, 32)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "Invalid device ID",
		})
		return
	}
	
	db := database.GetDB()
	var device models.Device
	
	// 查询设备并验证所有权
	if err := db.Where("id = ? AND owner_id = ?", uint(deviceID), userID).First(&device).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{
			"error": "Device not found",
		})
		return
	}
	
	c.JSON(http.StatusOK, gin.H{
		"status": 1,
		"data":   device,
	})
}

// CreateDevice 创建设备
// @Summary 创建新设备
// @Description 创建一个新的IoT设备
// @Tags 设备管理
// @Security BearerAuth
// @Accept json
// @Produce json
// @Param request body CreateDeviceRequest true "设备信息"
// @Success 201 {object} models.Device
// @Failure 400 {object} map[string]interface{}
// @Router /devices [post]
func (ctrl *DeviceController) CreateDevice(c *gin.Context) {
	userID := middleware.GetUserID(c)
	if userID == 0 {
		c.JSON(http.StatusUnauthorized, gin.H{
			"error": "Authentication required",
		})
		return
	}
	
	var req CreateDeviceRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error":   "Invalid request format",
			"details": err.Error(),
		})
		return
	}
	
	db := database.GetDB()
	
	// 检查设备ID是否已存在
	var existingDevice models.Device
	if err := db.Where("device_id = ?", req.DeviceID).First(&existingDevice).Error; err == nil {
		c.JSON(http.StatusConflict, gin.H{
			"error": "Device ID already exists",
		})
		return
	}
	
	// 创建设备
	device := models.Device{
		DeviceID: req.DeviceID,
		Name:     req.Name,
		Type:     req.Type,
		Location: req.Location,
		Config:   req.Config,
		Status:   "offline",
		OwnerID:  userID,
	}
	
	if err := db.Create(&device).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "Failed to create device",
		})
		return
	}
	
	// 清除缓存
	cache := database.NewCache()
	cache.Delete(c, database.Keys.DeviceList(userID))
	
	// 通过WebSocket通知设备创建
	if websocket.DefaultManager != nil {
		message := websocket.Message{
			Type: websocket.TypeNotification,
			Data: map[string]interface{}{
				"action": "device_created",
				"device": device,
			},
			Timestamp: time.Now(),
		}
		websocket.DefaultManager.SendToUser(userID, message)
	}
	
	c.JSON(http.StatusCreated, gin.H{
		"status": 1,
		"msg":    "设备创建成功",
		"data":   device,
	})
}

// UpdateDevice 更新设备
// @Summary 更新设备信息
// @Description 更新设备的基本信息
// @Tags 设备管理
// @Security BearerAuth
// @Accept json
// @Produce json
// @Param id path int true "设备ID"
// @Param request body UpdateDeviceRequest true "更新信息"
// @Success 200 {object} models.Device
// @Failure 400 {object} map[string]interface{}
// @Router /devices/{id} [put]
func (ctrl *DeviceController) UpdateDevice(c *gin.Context) {
	userID := middleware.GetUserID(c)
	deviceID, err := strconv.ParseUint(c.Param("id"), 10, 32)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "Invalid device ID",
		})
		return
	}
	
	var req UpdateDeviceRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error":   "Invalid request format",
			"details": err.Error(),
		})
		return
	}
	
	db := database.GetDB()
	var device models.Device
	
	// 查询设备并验证所有权
	if err := db.Where("id = ? AND owner_id = ?", uint(deviceID), userID).First(&device).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{
			"error": "Device not found",
		})
		return
	}
	
	// 更新设备信息
	if req.Name != "" {
		device.Name = req.Name
	}
	if req.Location != nil {
		device.Location = req.Location
	}
	if req.Config != nil {
		device.Config = req.Config
	}
	
	if err := db.Save(&device).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "Failed to update device",
		})
		return
	}
	
	// 清除缓存
	cache := database.NewCache()
	cache.Delete(c, database.Keys.Device(device.DeviceID))
	cache.Delete(c, database.Keys.DeviceList(userID))
	
	c.JSON(http.StatusOK, gin.H{
		"status": 1,
		"msg":    "设备更新成功",
		"data":   device,
	})
}

// DeleteDevice 删除设备
// @Summary 删除设备
// @Description 删除指定的设备
// @Tags 设备管理
// @Security BearerAuth
// @Produce json
// @Param id path int true "设备ID"
// @Success 200 {object} map[string]interface{}
// @Failure 404 {object} map[string]interface{}
// @Router /devices/{id} [delete]
func (ctrl *DeviceController) DeleteDevice(c *gin.Context) {
	userID := middleware.GetUserID(c)
	deviceID, err := strconv.ParseUint(c.Param("id"), 10, 32)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "Invalid device ID",
		})
		return
	}
	
	db := database.GetDB()
	var device models.Device
	
	// 查询设备并验证所有权
	if err := db.Where("id = ? AND owner_id = ?", uint(deviceID), userID).First(&device).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{
			"error": "Device not found",
		})
		return
	}
	
	// 删除相关的传感器数据
	db.Where("device_id = ?", device.DeviceID).Delete(&models.SensorData{})
	
	// 删除设备
	if err := db.Delete(&device).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "Failed to delete device",
		})
		return
	}
	
	// 清除缓存
	cache := database.NewCache()
	cache.Delete(c, database.Keys.Device(device.DeviceID))
	cache.Delete(c, database.Keys.DeviceList(userID))
	
	c.JSON(http.StatusOK, gin.H{
		"status": 1,
		"msg":    "设备删除成功",
	})
}

// GetDeviceData 获取设备实时数据
// @Summary 获取设备实时数据
// @Description 获取设备的最新传感器数据
// @Tags 设备管理
// @Security BearerAuth
// @Produce json
// @Param device_id path string true "设备ID"
// @Success 200 {object} models.SensorData
// @Router /devices/{device_id}/data [get]
func (ctrl *DeviceController) GetDeviceData(c *gin.Context) {
	userID := middleware.GetUserID(c)
	deviceID := c.Param("device_id")
	
	// 验证设备所有权
	db := database.GetDB()
	var device models.Device
	if err := db.Where("device_id = ? AND owner_id = ?", deviceID, userID).First(&device).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{
			"error": "Device not found",
		})
		return
	}
	
	// 获取最新的传感器数据
	var sensorData models.SensorData
	if err := db.Where("device_id = ?", deviceID).Order("timestamp DESC").First(&sensorData).Error; err != nil {
		c.JSON(http.StatusOK, gin.H{
			"status": 1,
			"data":   nil,
			"msg":    "No data available",
		})
		return
	}
	
	c.JSON(http.StatusOK, gin.H{
		"status": 1,
		"data":   sensorData,
	})
}

// GetDeviceHistory 获取设备历史数据
// @Summary 获取设备历史数据
// @Description 获取设备的历史传感器数据
// @Tags 设备管理
// @Security BearerAuth
// @Produce json
// @Param device_id path string true "设备ID"
// @Param start_time query string false "开始时间" format(date-time)
// @Param end_time query string false "结束时间" format(date-time)
// @Param limit query int false "数据条数限制" default(100)
// @Success 200 {object} []models.SensorData
// @Router /devices/{device_id}/history [get]
func (ctrl *DeviceController) GetDeviceHistory(c *gin.Context) {
	userID := middleware.GetUserID(c)
	deviceID := c.Param("device_id")
	
	// 验证设备所有权
	db := database.GetDB()
	var device models.Device
	if err := db.Where("device_id = ? AND owner_id = ?", deviceID, userID).First(&device).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{
			"error": "Device not found",
		})
		return
	}
	
	// 解析时间参数
	query := db.Where("device_id = ?", deviceID)
	
	if startTime := c.Query("start_time"); startTime != "" {
		if t, err := time.Parse(time.RFC3339, startTime); err == nil {
			query = query.Where("timestamp >= ?", t)
		}
	}
	
	if endTime := c.Query("end_time"); endTime != "" {
		if t, err := time.Parse(time.RFC3339, endTime); err == nil {
			query = query.Where("timestamp <= ?", t)
		}
	}
	
	// 限制数据条数
	limit, _ := strconv.Atoi(c.DefaultQuery("limit", "100"))
	if limit > 1000 {
		limit = 1000
	}
	
	var sensorData []models.SensorData
	if err := query.Order("timestamp DESC").Limit(limit).Find(&sensorData).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "Failed to fetch sensor data",
		})
		return
	}
	
	c.JSON(http.StatusOK, gin.H{
		"status": 1,
		"data":   sensorData,
	})
}

// PostDeviceData 接收设备上报的数据
// @Summary 设备数据上报
// @Description IoT设备上报传感器数据的接口
// @Tags 设备数据
// @Accept json
// @Produce json
// @Param device_id path string true "设备ID"
// @Param data body map[string]interface{} true "传感器数据"
// @Success 200 {object} map[string]interface{}
// @Router /devices/{device_id}/data [post]
func (ctrl *DeviceController) PostDeviceData(c *gin.Context) {
	deviceID := c.Param("device_id")
	
	var data models.JSONB
	if err := c.ShouldBindJSON(&data); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "Invalid data format",
		})
		return
	}
	
	db := database.GetDB()
	
	// 验证设备是否存在
	var device models.Device
	if err := db.Where("device_id = ?", deviceID).First(&device).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{
			"error": "Device not found",
		})
		return
	}
	
	// 保存传感器数据
	sensorData := models.SensorData{
		DeviceID:  deviceID,
		Data:      data,
		Timestamp: time.Now(),
	}
	
	if err := db.Create(&sensorData).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "Failed to save sensor data",
		})
		return
	}
	
	// 更新设备最后通信时间和状态
	now := time.Now()
	device.LastSeen = &now
	device.Status = "online"
	db.Save(&device)
	
	// 通过WebSocket实时推送数据
	if websocket.DefaultManager != nil {
		message := websocket.Message{
			Type: websocket.TypeDeviceData,
			Data: map[string]interface{}{
				"device_id": deviceID,
				"data":      data,
				"timestamp": sensorData.Timestamp,
			},
			Timestamp: time.Now(),
		}
		
		// 推送给订阅该设备的客户端
		websocket.DefaultManager.SendToDevice(deviceID, message)
	}
	
	c.JSON(http.StatusOK, gin.H{
		"status": 1,
		"msg":    "数据接收成功",
	})
}

// GetDeviceTypes 获取设备类型列表
// @Summary 获取设备类型列表
// @Description 获取系统支持的所有设备类型
// @Tags 设备管理
// @Produce json
// @Success 200 {object} map[string]interface{}
// @Router /devices/types [get]
func (ctrl *DeviceController) GetDeviceTypes(c *gin.Context) {
	types := make([]map[string]interface{}, 0, len(models.DeviceTypeNames))
	
	for typeID, typeName := range models.DeviceTypeNames {
		types = append(types, map[string]interface{}{
			"id":   int(typeID),
			"name": typeName,
		})
	}
	
	c.JSON(http.StatusOK, gin.H{
		"status": 1,
		"data":   types,
	})
}

// GetDeviceStats 获取设备统计信息
// @Summary 获取设备统计信息
// @Description 获取用户设备的统计信息
// @Tags 设备管理
// @Security BearerAuth
// @Produce json
// @Success 200 {object} []models.DeviceStatus
// @Router /devices/stats [get]
func (ctrl *DeviceController) GetDeviceStats(c *gin.Context) {
	userID := middleware.GetUserID(c)
	if userID == 0 {
		c.JSON(http.StatusUnauthorized, gin.H{
			"error": "Authentication required",
		})
		return
	}
	
	db := database.GetDB()
	var stats []models.DeviceStatus
	
	// 统计各类型设备数量
	for typeID, typeName := range models.DeviceTypeNames {
		var total, online int64
		
		// 统计总数
		db.Model(&models.Device{}).Where("owner_id = ? AND type = ?", userID, typeID).Count(&total)
		
		// 统计在线数量（最近5分钟有数据）
		fiveMinutesAgo := time.Now().Add(-5 * time.Minute)
		db.Model(&models.Device{}).Where("owner_id = ? AND type = ? AND last_seen > ?", 
			userID, typeID, fiveMinutesAgo).Count(&online)
		
		stats = append(stats, models.DeviceStatus{
			Type:       typeID,
			TypeName:   typeName,
			Total:      total,
			Online:     online,
			Offline:    total - online,
			LastUpdate: time.Now(),
		})
	}
	
	c.JSON(http.StatusOK, gin.H{
		"status": 1,
		"data":   stats,
	})
}