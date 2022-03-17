package com.imooc.appoint.service;

import com.imooc.appoint.dto.JsonResponse;
import com.vlis.apm.demo.utils.DemoUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import java.util.*;
import java.io.BufferedReader;
import java.io.FileReader;
import java.io.File;
import java.io.FileNotFoundException;

public class FdRunOutService {
    private static final Logger logger = LoggerFactory.getLogger(FdRunOutService.class);
    public Object run(Map<String, Object> params) {
        try {
            String root = System.getProperty("user.dir");
            String filePath = root + File.separator + "README.md";
            logger.info("FDRunOutService filePath: ");

            for (int i = 0; i < 100000; i++) {
                /// usr/local/tomcat/README.md
                BufferedReader br = new BufferedReader(new FileReader(filePath));
            }
            Thread.sleep(1000);
        } catch (Exception e) {
            logger.info("FDRunOutService run error: " + e.getMessage());
            return creatEntityWithBlock(500, -1L, "msg:" + e.getMessage());
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

