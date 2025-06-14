import request from '@/utils/request';

/**
 * 获取当前工人的工资记录
 * @param {object} params - 查询参数
 * @param {string} [params.start_date] - 开始月份 (YYYY-MM)
 * @param {string} [params.end_date] - 结束月份 (YYYY-MM)
 */
export function getMyWages(params) {
  return request({
    url: '/workers/my-wages',
    method: 'get',
    params
  });
} 