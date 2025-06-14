import request from '@/utils/request';

/**
 * 获取当前登录工人的个人资料
 */
export function getMyProfile() {
  return request({
    url: '/workers/me',
    method: 'get'
  });
}

/**
 * 更新当前登录工人的个人资料
 * @param {object} data - 个人资料数据
 */
export function updateMyProfile(data) {
  return request({
    url: '/workers/me',
    method: 'put',
    data
  });
}

/**
 * 修改当前登录工人的密码
 * @param {object} data - 密码数据
 * @param {string} data.old_password - 旧密码
 * @param {string} data.new_password - 新密码
 */
export function changeMyPassword(data) {
  return request({
    url: '/workers/me/password',
    method: 'put',
    data
  });
} 