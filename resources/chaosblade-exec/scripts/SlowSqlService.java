package com.imooc.appoint.service;

import com.imooc.appoint.dto.JsonResponse;
import com.imooc.appoint.service.Impl.PracticeServiceImpl;
import com.vlis.apm.demo.utils.DemoUtils;
import com.vlis.apm.demo.utils.MysqlDBUtil;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import java.sql.*;
import java.util.*;

public class SlowSqlService {
    private static final Logger logger = LoggerFactory.getLogger(SlowSqlService.class);
    public Object run(Map<String, Object> params) {
        logger.info("SlowSqlService run method. ");
        String sql="select * from k8s_container c LEFT JOIN process_status e on e.node_name=c.name order by c.id desc limit 0,10";
        logger.info("SlowSqlService exec mysql: " + sql);
        List<Map<String, Object>> dataList = new ArrayList<>();
        Connection conn = MysqlDBUtil.getDBConnection();
        PreparedStatement preparedStatement = null;
        ResultSet resultSet = null;
        try {
            preparedStatement = conn.prepareStatement(sql);
            resultSet = MysqlDBUtil.doSelect(preparedStatement);
            while (resultSet.next()) {
                dataList = getMetaData(resultSet);
            }
            return PracticeServiceImpl.creatEntityWithBlock(200, -1L, dataList);
        } catch (Exception e) {
            logger.error("mysqlQuery failed. ", e);
            return  creatEntityWithBlock(500, -1L, "msg:" + e.getMessage());
        } finally {
            MysqlDBUtil.closeConnection(resultSet, preparedStatement, conn);
        }
    }
    public static HttpEntity<JsonResponse> creatEntityWithBlock(int statusCode, Long blockTime, Object data) {
        HttpStatus httpStatus = HttpStatus.valueOf(statusCode);
        DemoUtils.showCurrentTime("Start creatEntityWithBlock");
        if (Objects.isNull(blockTime)) {
            blockTime = 500L;
        }
        DemoUtils.blockThread(blockTime);
        DemoUtils.showCurrentTime("End creatEntityWithBlock");
        ResponseEntity.BodyBuilder builder = ResponseEntity.status(httpStatus);
        HttpHeaders headers = new HttpHeaders();
        headers.set("Connection", "keep-alive");
        builder.headers(headers);
        if (data == null) {
            data = DemoUtils.defaultData();
        }
        return builder.body(JsonResponse.successResWithData(data));
    }

    private static List<Map<String, Object>> getMetaData(ResultSet resultSet) {
        List<String> columnNames = new ArrayList<>();
        List<Map<String, Object>> dataList = new ArrayList<>();
        // 关键一步：根据结果集获取元数据
        ResultSetMetaData metaData;
        try {
            metaData = resultSet.getMetaData();
            // 获取表中的列数
            int columnCount = metaData.getColumnCount();
            for (int i = 1; i <= columnCount; i++) {
                // 获取所有列名
                columnNames.add(metaData.getColumnName(i));
            }
            while (resultSet.next()) {
                Map<String, Object> columnData = new HashMap<>();
                // 根据所有列名，获取所有数据
                for (String columnName : columnNames) {
                    Object object = resultSet.getObject(columnName);
                    columnData.put(columnName, object);
                }
                dataList.add(columnData);
            }
        } catch (SQLException e) {
            logger.error("get SQL Exception. ", e);
        }
        return dataList;
    }
}
