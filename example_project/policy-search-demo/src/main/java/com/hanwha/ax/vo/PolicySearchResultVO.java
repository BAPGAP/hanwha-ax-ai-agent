package com.hanwha.ax.vo;

import lombok.Getter;
import lombok.Setter;
import lombok.ToString;

/**
 * 증권조회 결과 VO
 * 조회 결과 리스트의 각 행(Row)을 나타내는 객체
 */
@Getter
@Setter
@ToString
public class PolicySearchResultVO {

    /** 증권번호 */
    private String policyNo;

    /** 상품명 */
    private String productName;

    /** 상품코드 */
    private String productCode;

    /** 고객명 */
    private String customerName;

    /** 고객 주민등록번호 (마스킹 처리: 앞 6자리 + ******* 형태) */
    private String customerRrnMasked;

    /** 계약일자 (가입일자) */
    private String contractDate;

    /** 보험 시작일 */
    private String startDate;

    /** 보험 만기일 */
    private String endDate;

    /** 가입기간 (예: 20년) */
    private String contractPeriod;

    /** 월 보험료 (원) */
    private long monthlyPremium;

    /** 보장금액 (원) */
    private long coverageAmount;

    /** 납입주기 (월납/연납) */
    private String paymentCycle;

    /** 납입방법 (자동이체/카드) */
    private String paymentMethod;

    /** 계약상태 (정상/실효/해지/만기) */
    private String contractStatus;

    /** 계약상태 코드 */
    private String contractStatusCode;

    /** 담당 설계사명 */
    private String agentName;

    /** 담당 지점명 */
    private String branchName;

    /** 전체 건수 (페이징용) */
    private int totalCount;
}
