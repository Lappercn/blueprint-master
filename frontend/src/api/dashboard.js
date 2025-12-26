// 文件名：dashboard.js
import request from '../utils/request'

// 获取书籍统计
export const getBookStats = () => {
  return request({
    url: '/dashboard/stats/books',
    method: 'get'
  })
}

// 获取用户统计
export const getUserStats = () => {
  return request({
    url: '/dashboard/stats/users',
    method: 'get'
  })
}
