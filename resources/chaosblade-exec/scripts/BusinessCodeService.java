package com.imooc.appoint.service;

import com.imooc.appoint.dto.JsonResponse;
import com.imooc.appoint.service.Impl.PracticeServiceImpl;
import com.vlis.apm.demo.utils.DemoUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import java.util.*;

public class BusinessCodeService {
    private static final Logger logger = LoggerFactory.getLogger(PracticeServiceImpl.class);
    public Object run(Map<String, Object> params) {
        logger.info("BusinessCodeService run method. ");
        logger.info("BusinessCodeService business code error. ");
        try {
            int i = 1/0;
        } catch (Exception e) {
            return  creatEntityWithBlock(500, -1L, "msg:" + e.getMessage());
        }
        return null;
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
}
