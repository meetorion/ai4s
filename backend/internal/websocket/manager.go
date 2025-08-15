package websocket

import (
	"context"
	"encoding/json"
	"log"
	"net/http"
	"sync"
	"time"
	
	"github.com/gin-gonic/gin"
	"github.com/gorilla/websocket"
	"iot-platform-backend/internal/config"
)

// MessageType 消息类型
type MessageType string

const (
	TypeDeviceData   MessageType = "device_data"
	TypeDeviceStatus MessageType = "device_status" 
	TypeNotification MessageType = "notification"
	TypeHeartbeat    MessageType = "heartbeat"
	TypeSubscribe    MessageType = "subscribe"
	TypeUnsubscribe  MessageType = "unsubscribe"
	TypeError        MessageType = "error"
)

// Message WebSocket消息结构
type Message struct {
	Type      MessageType `json:"type"`
	Data      interface{} `json:"data,omitempty"`
	Error     string      `json:"error,omitempty"`
	Timestamp time.Time   `json:"timestamp"`
	ID        string      `json:"id,omitempty"`
}

// Client WebSocket客户端
type Client struct {
	ID       string
	UserID   uint
	Conn     *websocket.Conn
	Send     chan Message
	Manager  *Manager
	
	// 订阅信息
	Subscriptions map[string]bool // 订阅的设备ID
	mu           sync.RWMutex
}

// Manager WebSocket连接管理器
type Manager struct {
	clients    map[string]*Client
	register   chan *Client
	unregister chan *Client
	broadcast  chan Message
	
	// 按用户分组的客户端
	userClients map[uint]map[string]*Client
	
	mu sync.RWMutex
}

// NewManager 创建新的WebSocket管理器
func NewManager() *Manager {
	return &Manager{
		clients:     make(map[string]*Client),
		register:    make(chan *Client),
		unregister:  make(chan *Client),
		broadcast:   make(chan Message),
		userClients: make(map[uint]map[string]*Client),
	}
}

// Run 运行WebSocket管理器
func (m *Manager) Run() {
	for {
		select {
		case client := <-m.register:
			m.registerClient(client)
		case client := <-m.unregister:
			m.unregisterClient(client)
		case message := <-m.broadcast:
			m.broadcastMessage(message)
		}
	}
}

// registerClient 注册客户端
func (m *Manager) registerClient(client *Client) {
	m.mu.Lock()
	defer m.mu.Unlock()
	
	m.clients[client.ID] = client
	
	// 按用户分组
	if m.userClients[client.UserID] == nil {
		m.userClients[client.UserID] = make(map[string]*Client)
	}
	m.userClients[client.UserID][client.ID] = client
	
	log.Printf("Client registered: %s (User: %d)", client.ID, client.UserID)
	
	// 发送欢迎消息
	welcomeMsg := Message{
		Type:      TypeNotification,
		Data:      map[string]string{"message": "Connected successfully"},
		Timestamp: time.Now(),
	}
	
	select {
	case client.Send <- welcomeMsg:
	default:
		close(client.Send)
	}
}

// unregisterClient 注销客户端
func (m *Manager) unregisterClient(client *Client) {
	m.mu.Lock()
	defer m.mu.Unlock()
	
	if _, ok := m.clients[client.ID]; ok {
		delete(m.clients, client.ID)
		
		// 从用户分组中删除
		if userClients := m.userClients[client.UserID]; userClients != nil {
			delete(userClients, client.ID)
			if len(userClients) == 0 {
				delete(m.userClients, client.UserID)
			}
		}
		
		close(client.Send)
		log.Printf("Client unregistered: %s (User: %d)", client.ID, client.UserID)
	}
}

// broadcastMessage 广播消息
func (m *Manager) broadcastMessage(message Message) {
	m.mu.RLock()
	defer m.mu.RUnlock()
	
	for _, client := range m.clients {
		select {
		case client.Send <- message:
		default:
			close(client.Send)
			delete(m.clients, client.ID)
		}
	}
}

// SendToUser 发送消息给特定用户的所有连接
func (m *Manager) SendToUser(userID uint, message Message) {
	m.mu.RLock()
	defer m.mu.RUnlock()
	
	if userClients := m.userClients[userID]; userClients != nil {
		for _, client := range userClients {
			select {
			case client.Send <- message:
			default:
				close(client.Send)
			}
		}
	}
}

// SendToDevice 发送设备数据给订阅该设备的客户端
func (m *Manager) SendToDevice(deviceID string, message Message) {
	m.mu.RLock()
	defer m.mu.RUnlock()
	
	for _, client := range m.clients {
		client.mu.RLock()
		subscribed := client.Subscriptions[deviceID]
		client.mu.RUnlock()
		
		if subscribed {
			select {
			case client.Send <- message:
			default:
				close(client.Send)
			}
		}
	}
}

// Broadcast 广播消息给所有客户端
func (m *Manager) Broadcast(message Message) {
	m.broadcast <- message
}

// GetClientCount 获取在线客户端数量
func (m *Manager) GetClientCount() int {
	m.mu.RLock()
	defer m.mu.RUnlock()
	return len(m.clients)
}

// GetUserClientCount 获取特定用户的连接数量
func (m *Manager) GetUserClientCount(userID uint) int {
	m.mu.RLock()
	defer m.mu.RUnlock()
	
	if userClients := m.userClients[userID]; userClients != nil {
		return len(userClients)
	}
	return 0
}

// readPump 处理客户端发送的消息
func (c *Client) readPump() {
	defer func() {
		c.Manager.unregister <- c
		c.Conn.Close()
	}()
	
	// 设置读取参数
	c.Conn.SetReadLimit(config.AppConfig.WebSocket.MaxMessageSize)
	c.Conn.SetReadDeadline(time.Now().Add(60 * time.Second))
	c.Conn.SetPongHandler(func(string) error {
		c.Conn.SetReadDeadline(time.Now().Add(60 * time.Second))
		return nil
	})
	
	for {
		var msg Message
		if err := c.Conn.ReadJSON(&msg); err != nil {
			if websocket.IsUnexpectedCloseError(err, websocket.CloseGoingAway, websocket.CloseAbnormalClosure) {
				log.Printf("WebSocket error: %v", err)
			}
			break
		}
		
		c.handleMessage(msg)
	}
}

// writePump 处理向客户端发送消息
func (c *Client) writePump() {
	ticker := time.NewTicker(54 * time.Second)
	defer func() {
		ticker.Stop()
		c.Conn.Close()
	}()
	
	for {
		select {
		case message, ok := <-c.Send:
			c.Conn.SetWriteDeadline(time.Now().Add(10 * time.Second))
			if !ok {
				c.Conn.WriteMessage(websocket.CloseMessage, []byte{})
				return
			}
			
			if err := c.Conn.WriteJSON(message); err != nil {
				log.Printf("WebSocket write error: %v", err)
				return
			}
			
		case <-ticker.C:
			c.Conn.SetWriteDeadline(time.Now().Add(10 * time.Second))
			if err := c.Conn.WriteMessage(websocket.PingMessage, nil); err != nil {
				return
			}
		}
	}
}

// handleMessage 处理客户端消息
func (c *Client) handleMessage(msg Message) {
	switch msg.Type {
	case TypeSubscribe:
		c.handleSubscribe(msg)
	case TypeUnsubscribe:
		c.handleUnsubscribe(msg)
	case TypeHeartbeat:
		c.handleHeartbeat()
	default:
		log.Printf("Unknown message type: %s", msg.Type)
	}
}

// handleSubscribe 处理订阅消息
func (c *Client) handleSubscribe(msg Message) {
	if data, ok := msg.Data.(map[string]interface{}); ok {
		if deviceID, exists := data["device_id"]; exists {
			if deviceIDStr, ok := deviceID.(string); ok {
				c.mu.Lock()
				c.Subscriptions[deviceIDStr] = true
				c.mu.Unlock()
				
				log.Printf("Client %s subscribed to device %s", c.ID, deviceIDStr)
				
				// 发送确认消息
				response := Message{
					Type: TypeNotification,
					Data: map[string]string{
						"message":   "Subscribed successfully",
						"device_id": deviceIDStr,
					},
					Timestamp: time.Now(),
				}
				
				select {
				case c.Send <- response:
				default:
				}
			}
		}
	}
}

// handleUnsubscribe 处理取消订阅消息
func (c *Client) handleUnsubscribe(msg Message) {
	if data, ok := msg.Data.(map[string]interface{}); ok {
		if deviceID, exists := data["device_id"]; exists {
			if deviceIDStr, ok := deviceID.(string); ok {
				c.mu.Lock()
				delete(c.Subscriptions, deviceIDStr)
				c.mu.Unlock()
				
				log.Printf("Client %s unsubscribed from device %s", c.ID, deviceIDStr)
			}
		}
	}
}

// handleHeartbeat 处理心跳消息
func (c *Client) handleHeartbeat() {
	response := Message{
		Type:      TypeHeartbeat,
		Data:      map[string]string{"status": "alive"},
		Timestamp: time.Now(),
	}
	
	select {
	case c.Send <- response:
	default:
	}
}

// 全局WebSocket管理器实例
var DefaultManager *Manager

// Init 初始化WebSocket管理器
func Init() {
	DefaultManager = NewManager()
	go DefaultManager.Run()
}

// upgrader WebSocket升级器
var upgrader = websocket.Upgrader{
	ReadBufferSize:  1024,
	WriteBufferSize: 1024,
	CheckOrigin: func(r *http.Request) bool {
		// 在生产环境中应该检查Origin
		return true
	},
}

// HandleWebSocket 处理WebSocket连接
func HandleWebSocket(c *gin.Context) {
	// 从查询参数或JWT token中获取用户ID
	userID := getUserIDFromContext(c)
	
	conn, err := upgrader.Upgrade(c.Writer, c.Request, nil)
	if err != nil {
		log.Printf("WebSocket upgrade failed: %v", err)
		return
	}
	
	client := &Client{
		ID:            generateClientID(),
		UserID:        userID,
		Conn:          conn,
		Send:          make(chan Message, 256),
		Manager:       DefaultManager,
		Subscriptions: make(map[string]bool),
	}
	
	DefaultManager.register <- client
	
	// 启动读写协程
	go client.writePump()
	go client.readPump()
}

// generateClientID 生成客户端ID
func generateClientID() string {
	return time.Now().Format("20060102150405") + "-" + generateRandomString(8)
}

// generateRandomString 生成随机字符串
func generateRandomString(length int) string {
	const charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
	b := make([]byte, length)
	for i := range b {
		b[i] = charset[time.Now().UnixNano()%int64(len(charset))]
	}
	return string(b)
}

// getUserIDFromContext 从上下文中获取用户ID
func getUserIDFromContext(c *gin.Context) uint {
	if userID, exists := c.Get("user_id"); exists {
		if uid, ok := userID.(uint); ok {
			return uid
		}
	}
	return 0 // 匿名用户
}