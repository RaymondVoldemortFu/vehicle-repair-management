import request from '@/utils/request';

export function getWorkerOrders(params) {
  return request({
    url: '/repair-orders/worker-orders',
    method: 'get',
    params
  });
}

export function updateWorkerOrderStatus(orderId, statusData) {
  return request({
    url: `/repair-orders/worker-orders/${orderId}/status`,
    method: 'put',
    data: statusData
  });
}

export function getAvailableOrders(params) {
  return request({
    url: '/repair-orders/available',
    method: 'get',
    params
  });
}

export function acceptOrder(orderId) {
  return request({
    url: `/repair-orders/${orderId}/accept`,
    method: 'post'
  });
}

export function rejectOrder(orderId) {
  return request({
    url: `/repair-orders/${orderId}/reject`,
    method: 'put'
  });
}

/**
 * 工人完成订单并提交工时
 * @param {number} orderId - 订单ID
 * @param {object} data - 工时数据
 * @param {number} data.work_hours - 总工时
 * @param {number} data.overtime_hours - 加班工时
 * @param {string} [data.work_description] - 工作描述
 */
export function completeOrder(orderId, data) {
  return request({
    url: `/repair-orders/worker-orders/${orderId}/complete`,
    method: 'post',
    data
  });
} 