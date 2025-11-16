package com.codeassistant.user.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.codeassistant.user.entity.User;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;
import org.apache.ibatis.annotations.Update;

import java.time.LocalDateTime;

/**
 * 用户Mapper接口
 * 继承MyBatis-Plus的BaseMapper，自动获得CRUD方法
 *
 * @author Code Assistant Platform
 * @since 2025-11-16
 */
@Mapper
public interface UserMapper extends BaseMapper<User> {

    /**
     * 根据用户名查询用户（包含已删除用户）
     * 用于检查用户名是否已被使用
     *
     * @param username 用户名
     * @return 用户对象，不存在返回null
     */
    @Select("SELECT * FROM users WHERE username = #{username} LIMIT 1")
    User findByUsernameIncludeDeleted(@Param("username") String username);

    /**
     * 根据邮箱查询用户（包含已删除用户）
     * 用于检查邮箱是否已被使用
     *
     * @param email 邮箱
     * @return 用户对象，不存在返回null
     */
    @Select("SELECT * FROM users WHERE email = #{email} LIMIT 1")
    User findByEmailIncludeDeleted(@Param("email") String email);

    /**
     * 根据用户名查询活跃用户
     *
     * @param username 用户名
     * @return 用户对象，不存在或已删除返回null
     */
    @Select("SELECT * FROM users WHERE username = #{username} AND deleted = 0 LIMIT 1")
    User findByUsername(@Param("username") String username);

    /**
     * 根据邮箱查询活跃用户
     *
     * @param email 邮箱
     * @return 用户对象，不存在或已删除返回null
     */
    @Select("SELECT * FROM users WHERE email = #{email} AND deleted = 0 LIMIT 1")
    User findByEmail(@Param("email") String email);

    /**
     * 根据邮箱验证Token查询用户
     *
     * @param token 验证Token
     * @return 用户对象，不存在返回null
     */
    @Select("SELECT * FROM users WHERE email_verify_token = #{token} AND deleted = 0 LIMIT 1")
    User findByEmailVerifyToken(@Param("token") String token);

    /**
     * 更新用户最后登录信息
     *
     * @param userId 用户ID
     * @param loginTime 登录时间
     * @param loginIp 登录IP
     * @return 影响的行数
     */
    @Update("UPDATE users SET last_login_at = #{loginTime}, last_login_ip = #{loginIp}, updated_at = CURRENT_TIMESTAMP WHERE id = #{userId} AND deleted = 0")
    int updateLastLogin(@Param("userId") Long userId,
                        @Param("loginTime") LocalDateTime loginTime,
                        @Param("loginIp") String loginIp);

    /**
     * 激活用户邮箱
     *
     * @param userId 用户ID
     * @return 影响的行数
     */
    @Update("UPDATE users SET email_verified = TRUE, status = 'ACTIVE', email_verify_token = NULL, updated_at = CURRENT_TIMESTAMP WHERE id = #{userId} AND deleted = 0")
    int activateUserEmail(@Param("userId") Long userId);

    /**
     * 更新用户状态
     *
     * @param userId 用户ID
     * @param status 新状态
     * @return 影响的行数
     */
    @Update("UPDATE users SET status = #{status}, updated_at = CURRENT_TIMESTAMP WHERE id = #{userId} AND deleted = 0")
    int updateStatus(@Param("userId") Long userId, @Param("status") String status);

    /**
     * 统计用户数量（按状态）
     *
     * @param status 用户状态，null表示所有状态
     * @return 用户数量
     */
    @Select("<script>" +
            "SELECT COUNT(*) FROM users WHERE deleted = 0 " +
            "<if test='status != null'> AND status = #{status} </if>" +
            "</script>")
    long countByStatus(@Param("status") String status);
}
