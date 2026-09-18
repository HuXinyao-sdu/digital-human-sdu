import axios from 'axios'

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 30000
})

request.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error('API Error:', error.message)
    return Promise.reject(error)
  }
)

// 健康检查
export const healthCheck = () => request.get('/health')

// 问答接口
export const chat = (data) => request.post('/chat', data)

// 获取讲解脚本列表
export const getScripts = () => request.get('/content/scripts')

// 获取图库列表
export const getGallery = () => request.get('/content/gallery')

export default request
