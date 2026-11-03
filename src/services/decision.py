from src.domain.contracts import ModelPrediction, MonthlyObservation, RiskDecision, Severity


def assess_risk(observation: MonthlyObservation, prediction: ModelPrediction) -> RiskDecision:
    evidence: list[str] = []
    score = 0.0

    if observation.quality.status != "valid":
        evidence.append(f"Data quality is {observation.quality.status}; scientific interpretation is limited.")
        return RiskDecision(
            severity=Severity.LOW,
            score=0,
            evidence=evidence + observation.quality.reasons,
            recommendations=["Wait for adequate observations or inspect alternative SAR evidence."],
        )

    if prediction.residual <= -0.05:
        score += 30
        evidence.append(f"NDVI is {abs(prediction.residual):.3f} below the model expectation.")
    if prediction.anomaly_score >= 2:
        score += 25
        evidence.append(f"Vegetation anomaly score is {prediction.anomaly_score:.2f} standard units.")
    if observation.ndmi_mean is not None and observation.ndmi_mean < 0.35:
        score += 15
        evidence.append("Moisture index is below the provisional review threshold.")
    if observation.co_mean is not None and observation.co_mean > 0.04:
        score += 10
        evidence.append("CO is elevated and is treated as contextual, non-causal evidence.")
    if observation.vh_mean is not None and observation.vh_mean < -19:
        score += 15
        evidence.append("SAR VH backscatter is low enough to warrant cross-sensor inspection.")

    if score >= 70:
        severity = Severity.CRITICAL
    elif score >= 50:
        severity = Severity.HIGH
    elif score >= 25:
        severity = Severity.MODERATE
    else:
        severity = Severity.LOW

    recommendations = {
        Severity.LOW: ["Continue routine monitoring."],
        Severity.MODERATE: ["Review the next acquisition and compare optical and SAR imagery."],
        Severity.HIGH: ["Request expert image review and plan targeted field verification."],
        Severity.CRITICAL: ["Escalate for urgent expert review and field verification before external action."],
    }[severity]
    if not evidence:
        evidence.append("No material anomaly was detected by the current rule set.")
    return RiskDecision(
        severity=severity,
        score=min(score, 100),
        evidence=evidence,
        recommendations=recommendations,
        requires_human_review=severity >= Severity.HIGH,
    )
