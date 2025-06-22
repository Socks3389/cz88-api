package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"

	"github.com/tagphi/czdb-search-golang/pkg/db" // 使用czdb-search库解析纯真IP数据库
)

type Response struct {
	Data string `json:"data"`
}

func main() {
	// 数据库文件路径和密钥
	dbFile := "/root/api/data.db"
	dbKey := "Tfhi+ijvEd6QVK4YUIEElA=="

	// 初始化数据库搜索器
	dbSearcher := initializeDatabase(dbFile, dbKey)
	defer db.CloseDBSearcher(dbSearcher)

	// 设置路由
	http.HandleFunc("/query", func(w http.ResponseWriter, r *http.Request) {
		handleQuery(w, r, dbSearcher)
	})

	// 启动服务器
	startServer()
}

func initializeDatabase(dbFile, dbKey string) *db.DBSearcher {
	// 初始化数据库搜索器，使用内存模式
	dbSearcher, err := db.InitDBSearcher(dbFile, dbKey, db.MEMORY)
	if err != nil {
		log.Fatalf("初始化数据库搜索器失败: %v", err)
	}
	log.Printf("纯真IP数据库加载成功: %s", dbFile)
	return dbSearcher
}

func handleQuery(w http.ResponseWriter, r *http.Request, dbSearcher *db.DBSearcher) {
	// 获取查询参数中的IP
	ip := r.URL.Query().Get("ip")
	if ip == "" {
		http.Error(w, "缺少ip参数", http.StatusBadRequest)
		log.Println("请求失败: 缺少ip参数")
		return
	}

	// 搜索IP地址
	region, err := db.Search(ip, dbSearcher)
	if err != nil {
		http.Error(w, fmt.Sprintf("查询失败: %v", err), http.StatusInternalServerError)
		log.Printf("查询失败: IP=%s, 错误=%v\n", ip, err)
		return
	}

	// 构造JSON响应
	response := Response{Data: region}
	w.Header().Set("Content-Type", "application/json")
	if err := json.NewEncoder(w).Encode(response); err != nil {
		log.Printf("响应编码失败: %v\n", err)
	} else {
		log.Printf("查询成功: IP=%s, 数据=%s\n", ip, region)
	}
}

func startServer() {
	port := ":8080"
	log.Printf("纯真IP数据库API服务器启动，监听端口%s\n", port)
	log.Fatal(http.ListenAndServe(port, nil))
}

