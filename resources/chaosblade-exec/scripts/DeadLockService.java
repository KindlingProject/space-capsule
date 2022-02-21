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

public class DeadLockService {
    public static String obj1 = "obj1";
    public static String obj2 = "obj2";
    private static final Logger logger = LoggerFactory.getLogger(DeadLockService.class);

    public Object run(Map<String, Object> params) {
        logger.info("DeadLockService run method. ");
        logger.info("DeadLockService business code error. ");
        new Thread(() -> {
            try {
                logger.info("Lock1 running");
                while (true) {
                    synchronized (DeadLockService.obj1) {
                        logger.info("Lock1 lock obj1");
                        //获取obj1后先等一会儿，让Lock2有足够的时间锁住obj2
                        Thread.sleep(3000);
                        synchronized (DeadLockService.obj2) {
                            logger.info("Lock1 lock obj2");
                        }
                    }
                }
            } catch (Exception e) {
                e.printStackTrace();
            }
        }).start();
        try{
                logger.info("Lock2 running");
                while(true){
                    synchronized(DeadLockService.obj2){
                        logger.info("Lock2 lock obj2");
                        Thread.sleep(3000);
                        synchronized(DeadLockService.obj1){
                            logger.info("Lock2 lock obj1");
                        }
                    }
                }
            }catch(Exception e){
                e.printStackTrace();
            }
        return creatEntityWithBlock(200, -1L, "ok");
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

