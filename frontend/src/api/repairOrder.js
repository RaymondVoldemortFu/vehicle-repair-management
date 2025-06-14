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