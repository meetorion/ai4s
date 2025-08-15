package database

import (
	"context"
	"fmt"
	"time"
	"encoding/json"
	
	"github.com/redis/go-redis/v9"
)

var RedisClient *redis.Client

// RedisConfig Redis配置
type RedisConfig struct {
	Host     string
	Port     string
	Password string
	DB       int
}

// ConnectRedis 连接Redis
func ConnectRedis(cfg *RedisConfig) error {
	addr := fmt.Sprintf("%s:%s", cfg.Host, cfg.Port)
	
	RedisClient = redis.NewClient(&redis.Options{
		Addr:     addr,
		Password: cfg.Password,
		DB:       cfg.DB,
		
		// 连接池配置
		PoolSize:        10,
		PoolTimeout:     30 * time.Second,
		IdleTimeout:     5 * time.Minute,
		IdleCheckFrequency: time.Minute,
		
		// 重试配置
		MaxRetries:      3,
		MinRetryBackoff: 8 * time.Millisecond,
		MaxRetryBackoff: 512 * time.Millisecond,
	})
	
	// 测试连接
	ctx := context.Background()
	_, err := RedisClient.Ping(ctx).Result()
	if err != nil {
		return fmt.Errorf("failed to connect to Redis: %w", err)
	}
	
	fmt.Println("Redis connected successfully")
	return nil
}

// Cache Redis缓存操作封装
type Cache struct {
	client *redis.Client
}

// NewCache 创建缓存实例
func NewCache() *Cache {
	return &Cache{client: RedisClient}
}

// Set 设置缓存
func (c *Cache) Set(ctx context.Context, key string, value interface{}, expiration time.Duration) error {
	jsonValue, err := json.Marshal(value)
	if err != nil {
		return err
	}
	
	return c.client.Set(ctx, key, jsonValue, expiration).Err()
}

// Get 获取缓存
func (c *Cache) Get(ctx context.Context, key string, dest interface{}) error {
	val, err := c.client.Get(ctx, key).Result()
	if err != nil {
		return err
	}
	
	return json.Unmarshal([]byte(val), dest)
}

// Delete 删除缓存
func (c *Cache) Delete(ctx context.Context, keys ...string) error {
	return c.client.Del(ctx, keys...).Err()
}

// Exists 检查缓存是否存在
func (c *Cache) Exists(ctx context.Context, key string) (bool, error) {
	result, err := c.client.Exists(ctx, key).Result()
	return result > 0, err
}

// Expire 设置过期时间
func (c *Cache) Expire(ctx context.Context, key string, expiration time.Duration) error {
	return c.client.Expire(ctx, key, expiration).Err()
}

// HSet 哈希表设置
func (c *Cache) HSet(ctx context.Context, key string, field string, value interface{}) error {
	jsonValue, err := json.Marshal(value)
	if err != nil {
		return err
	}
	
	return c.client.HSet(ctx, key, field, jsonValue).Err()
}

// HGet 哈希表获取
func (c *Cache) HGet(ctx context.Context, key string, field string, dest interface{}) error {
	val, err := c.client.HGet(ctx, key, field).Result()
	if err != nil {
		return err
	}
	
	return json.Unmarshal([]byte(val), dest)
}

// HGetAll 获取哈希表所有字段
func (c *Cache) HGetAll(ctx context.Context, key string) (map[string]string, error) {
	return c.client.HGetAll(ctx, key).Result()
}

// HDel 删除哈希表字段
func (c *Cache) HDel(ctx context.Context, key string, fields ...string) error {
	return c.client.HDel(ctx, key, fields...).Err()
}

// ZAdd 有序集合添加
func (c *Cache) ZAdd(ctx context.Context, key string, score float64, member interface{}) error {
	return c.client.ZAdd(ctx, key, redis.Z{
		Score:  score,
		Member: member,
	}).Err()
}

// ZRangeByScore 按分数范围获取有序集合
func (c *Cache) ZRangeByScore(ctx context.Context, key string, min, max string, offset, count int64) ([]string, error) {
	return c.client.ZRangeByScore(ctx, key, &redis.ZRangeBy{
		Min:    min,
		Max:    max,
		Offset: offset,
		Count:  count,
	}).Result()
}

// ZRem 删除有序集合成员
func (c *Cache) ZRem(ctx context.Context, key string, members ...interface{}) error {
	return c.client.ZRem(ctx, key, members...).Err()
}

// Publish 发布消息
func (c *Cache) Publish(ctx context.Context, channel string, message interface{}) error {
	jsonMessage, err := json.Marshal(message)
	if err != nil {
		return err
	}
	
	return c.client.Publish(ctx, channel, jsonMessage).Err()
}

// Subscribe 订阅消息
func (c *Cache) Subscribe(ctx context.Context, channels ...string) *redis.PubSub {
	return c.client.Subscribe(ctx, channels...)
}

// Close 关闭Redis连接
func CloseRedis() error {
	if RedisClient != nil {
		return RedisClient.Close()
	}
	return nil
}

// RedisHealth Redis健康检查
func RedisHealth() error {
	if RedisClient == nil {
		return fmt.Errorf("Redis client not initialized")
	}
	
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	
	_, err := RedisClient.Ping(ctx).Result()
	return err
}

// RedisStats 获取Redis统计信息
func RedisStats() (map[string]interface{}, error) {
	if RedisClient == nil {
		return nil, fmt.Errorf("Redis client not initialized")
	}
	
	ctx := context.Background()
	
	info, err := RedisClient.Info(ctx, "stats").Result()
	if err != nil {
		return nil, err
	}
	
	stats := RedisClient.PoolStats()
	
	return map[string]interface{}{
		"info":        info,
		"hits":        stats.Hits,
		"misses":      stats.Misses,
		"timeouts":    stats.Timeouts,
		"total_conns": stats.TotalConns,
		"idle_conns":  stats.IdleConns,
		"stale_conns": stats.StaleConns,
	}, nil
}

// 缓存键前缀常量
const (
	UserCachePrefix    = "user:"
	DeviceCachePrefix  = "device:"
	ProjectCachePrefix = "project:"
	DataCachePrefix    = "data:"
	SessionPrefix      = "session:"
)

// CacheKeys 生成缓存键的辅助函数
type CacheKeys struct{}

func (CacheKeys) User(id uint) string {
	return fmt.Sprintf("%s%d", UserCachePrefix, id)
}

func (CacheKeys) Device(deviceID string) string {
	return fmt.Sprintf("%s%s", DeviceCachePrefix, deviceID)
}

func (CacheKeys) Project(id uint) string {
	return fmt.Sprintf("%s%d", ProjectCachePrefix, id)
}

func (CacheKeys) SensorData(deviceID string, date string) string {
	return fmt.Sprintf("%s%s:%s", DataCachePrefix, deviceID, date)
}

func (CacheKeys) Session(sessionID string) string {
	return fmt.Sprintf("%s%s", SessionPrefix, sessionID)
}

func (CacheKeys) DeviceList(userID uint) string {
	return fmt.Sprintf("device_list:%d", userID)
}

func (CacheKeys) ProjectList(userID uint) string {
	return fmt.Sprintf("project_list:%d", userID)
}

// 全局缓存键实例
var Keys CacheKeys