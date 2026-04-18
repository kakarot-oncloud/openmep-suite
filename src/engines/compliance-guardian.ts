export type Severity = "error" | "warning" | "info";
export type Region = "DEWA" | "IS" | "AS_NZS" | "IEC" | "NFPA";
export type ModuleType =
  | "electrical"
  | "hvac"
  | "fire_protection"
  | "plumbing"
  | "structural";

export interface ComplianceViolation {
  severity: Severity;
  module: ModuleType;
  parameter: string;
  actualValue: number | string;
  limit: number | string;
  unit?: string;
  standardClause: string;
  message: string;
}

export interface ModuleResult {
  module: ModuleType;
  region: Region;
  parameters: Record<string, number | string>;
}

type RuleKey = `${Region}:${ModuleType}:${string}`;

interface RuleDefinition {
  severity: Severity;
  standardClause: string;
  check: (params: Record<string, number | string>) => ComplianceViolation | null;
}

const rules: Map<RuleKey, RuleDefinition> = new Map();

function addRule(
  region: Region,
  module: ModuleType,
  paramKey: string,
  rule: RuleDefinition,
) {
  rules.set(`${region}:${module}:${paramKey}`, rule);
}

addRule("DEWA", "electrical", "voltage_drop_percent", {
  severity: "error",
  standardClause: "DEWA Technical Guidelines §4.3.2",
  check(params) {
    const val = Number(params["voltage_drop_percent"]);
    const limit = 2.5;
    if (isNaN(val)) return null;
    if (val > limit) {
      return {
        severity: "error",
        module: "electrical",
        parameter: "voltage_drop_percent",
        actualValue: val,
        limit,
        unit: "%",
        standardClause: "DEWA Technical Guidelines §4.3.2",
        message: `Voltage drop ${val}% exceeds DEWA limit of ${limit}% — check conductor sizing on the affected circuit.`,
      };
    }
    return null;
  },
});

addRule("IS", "electrical", "voltage_drop_percent", {
  severity: "error",
  standardClause: "IS 732 §6.4",
  check(params) {
    const val = Number(params["voltage_drop_percent"]);
    const limit = 3.0;
    if (isNaN(val)) return null;
    if (val > limit) {
      return {
        severity: "error",
        module: "electrical",
        parameter: "voltage_drop_percent",
        actualValue: val,
        limit,
        unit: "%",
        standardClause: "IS 732 §6.4",
        message: `Voltage drop ${val}% exceeds IS limit of ${limit}% — review feeder cable cross-section.`,
      };
    }
    return null;
  },
});

addRule("AS_NZS", "electrical", "voltage_drop_percent", {
  severity: "error",
  standardClause: "AS/NZS 3000:2018 §3.6.2",
  check(params) {
    const val = Number(params["voltage_drop_percent"]);
    const limit = 5.0;
    if (isNaN(val)) return null;
    if (val > limit) {
      return {
        severity: "error",
        module: "electrical",
        parameter: "voltage_drop_percent",
        actualValue: val,
        limit,
        unit: "%",
        standardClause: "AS/NZS 3000:2018 §3.6.2",
        message: `Voltage drop ${val}% exceeds AS/NZS limit of ${limit}%.`,
      };
    }
    return null;
  },
});

addRule("DEWA", "electrical", "cable_ampacity_headroom_percent", {
  severity: "warning",
  standardClause: "DEWA Technical Guidelines §4.5.1",
  check(params) {
    const val = Number(params["cable_ampacity_headroom_percent"]);
    const minHeadroom = 10;
    if (isNaN(val)) return null;
    if (val < minHeadroom) {
      return {
        severity: "warning",
        module: "electrical",
        parameter: "cable_ampacity_headroom_percent",
        actualValue: val,
        limit: minHeadroom,
        unit: "%",
        standardClause: "DEWA Technical Guidelines §4.5.1",
        message: `Cable ampacity headroom is ${val}%, below the recommended ${minHeadroom}% — consider upsizing the conductor.`,
      };
    }
    return null;
  },
});

addRule("IEC", "electrical", "cable_ampacity_headroom_percent", {
  severity: "warning",
  standardClause: "IEC 60364-5-52 §523",
  check(params) {
    const val = Number(params["cable_ampacity_headroom_percent"]);
    const minHeadroom = 10;
    if (isNaN(val)) return null;
    if (val < minHeadroom) {
      return {
        severity: "warning",
        module: "electrical",
        parameter: "cable_ampacity_headroom_percent",
        actualValue: val,
        limit: minHeadroom,
        unit: "%",
        standardClause: "IEC 60364-5-52 §523",
        message: `Cable ampacity headroom is ${val}%, below recommended ${minHeadroom}%.`,
      };
    }
    return null;
  },
});

addRule("DEWA", "hvac", "cooling_load_vs_equipment_ratio", {
  severity: "error",
  standardClause: "ASHRAE 90.1-2019 §6.4 / DEWA Circular 2023-04",
  check(params) {
    const val = Number(params["cooling_load_vs_equipment_ratio"]);
    if (isNaN(val)) return null;
    if (val > 1.15) {
      return {
        severity: "error",
        module: "hvac",
        parameter: "cooling_load_vs_equipment_ratio",
        actualValue: val,
        limit: 1.15,
        standardClause: "ASHRAE 90.1-2019 §6.4 / DEWA Circular 2023-04",
        message: `Cooling load to equipment capacity ratio is ${val.toFixed(2)}, exceeding the 1.15 maximum — equipment is undersized.`,
      };
    }
    if (val < 0.8) {
      return {
        severity: "warning",
        module: "hvac",
        parameter: "cooling_load_vs_equipment_ratio",
        actualValue: val,
        limit: 0.8,
        standardClause: "ASHRAE 90.1-2019 §6.4 / DEWA Circular 2023-04",
        message: `Cooling equipment appears oversized (ratio ${val.toFixed(2)} < 0.80) — review equipment selection.`,
      };
    }
    return null;
  },
});

addRule("NFPA", "fire_protection", "sprinkler_coverage_density_mm_per_min", {
  severity: "error",
  standardClause: "NFPA 13 §19.3.3",
  check(params) {
    const val = Number(params["sprinkler_coverage_density_mm_per_min"]);
    const hazardGroup = String(params["hazard_group"] ?? "ordinary");
    const limits: Record<string, number> = {
      light: 4.1,
      ordinary: 6.1,
      extra: 12.2,
    };
    const limit = limits[hazardGroup] ?? limits["ordinary"];
    if (isNaN(val)) return null;
    if (val < limit) {
      return {
        severity: "error",
        module: "fire_protection",
        parameter: "sprinkler_coverage_density_mm_per_min",
        actualValue: val,
        limit,
        unit: "mm/min",
        standardClause: "NFPA 13 §19.3.3",
        message: `Sprinkler design density ${val} mm/min is below the NFPA 13 minimum of ${limit} mm/min for ${hazardGroup} hazard occupancy.`,
      };
    }
    return null;
  },
});

addRule("NFPA", "fire_protection", "fire_pump_residual_pressure_bar", {
  severity: "error",
  standardClause: "NFPA 20 §4.26",
  check(params) {
    const val = Number(params["fire_pump_residual_pressure_bar"]);
    const limit = 4.5;
    if (isNaN(val)) return null;
    if (val < limit) {
      return {
        severity: "error",
        module: "fire_protection",
        parameter: "fire_pump_residual_pressure_bar",
        actualValue: val,
        limit,
        unit: "bar",
        standardClause: "NFPA 20 §4.26",
        message: `Fire pump residual pressure ${val} bar is below the NFPA 20 minimum of ${limit} bar at peak demand.`,
      };
    }
    return null;
  },
});

addRule("IEC", "electrical", "power_factor", {
  severity: "warning",
  standardClause: "IEC 60038 / Utility Grid Code §5.2",
  check(params) {
    const val = Number(params["power_factor"]);
    const limit = 0.9;
    if (isNaN(val)) return null;
    if (val < limit) {
      return {
        severity: "warning",
        module: "electrical",
        parameter: "power_factor",
        actualValue: val,
        limit,
        standardClause: "IEC 60038 / Utility Grid Code §5.2",
        message: `Power factor ${val} is below the utility minimum of ${limit} — consider power factor correction capacitors.`,
      };
    }
    return null;
  },
});

addRule("DEWA", "electrical", "power_factor", {
  severity: "warning",
  standardClause: "DEWA Technical Guidelines §3.8",
  check(params) {
    const val = Number(params["power_factor"]);
    const limit = 0.9;
    if (isNaN(val)) return null;
    if (val < limit) {
      return {
        severity: "warning",
        module: "electrical",
        parameter: "power_factor",
        actualValue: val,
        limit,
        standardClause: "DEWA Technical Guidelines §3.8",
        message: `Power factor ${val} is below the DEWA minimum of ${limit}.`,
      };
    }
    return null;
  },
});

addRule("NFPA", "hvac", "exhaust_air_changes_per_hour", {
  severity: "info",
  standardClause: "NFPA 92 §7.3.2",
  check(params) {
    const val = Number(params["exhaust_air_changes_per_hour"]);
    const limit = 6;
    if (isNaN(val)) return null;
    if (val < limit) {
      return {
        severity: "info",
        module: "hvac",
        parameter: "exhaust_air_changes_per_hour",
        actualValue: val,
        limit,
        unit: "ACH",
        standardClause: "NFPA 92 §7.3.2",
        message: `Smoke exhaust rate ${val} ACH may be insufficient — NFPA 92 recommends ≥ ${limit} ACH for smoke control zones.`,
      };
    }
    return null;
  },
});

export interface CheckResult {
  parameter: string;
  module: ModuleType;
  region: Region;
  severity: Severity;
  standardClause: string;
  status: "pass" | "fail";
  message?: string;
}

export function getAllCheckResults(moduleResults: ModuleResult[]): CheckResult[] {
  const results: CheckResult[] = [];

  for (const result of moduleResults) {
    const { region, module, parameters } = result;

    for (const [key, rule] of rules.entries()) {
      const [ruleRegion, ruleModule, paramKey] = key.split(":") as [Region, ModuleType, string];
      if (ruleRegion !== region || ruleModule !== module) continue;
      if (!(paramKey in parameters)) continue;

      const violation = rule.check(parameters);
      results.push({
        parameter: paramKey,
        module,
        region,
        severity: violation ? violation.severity : rule.severity,
        standardClause: violation ? violation.standardClause : rule.standardClause,
        status: violation ? "fail" : "pass",
        message: violation?.message,
      });
    }
  }

  return results;
}

export function runComplianceCheck(
  moduleResults: ModuleResult[],
): ComplianceViolation[] {
  const violations: ComplianceViolation[] = [];

  for (const result of moduleResults) {
    const { region, module, parameters } = result;

    for (const [key, rule] of rules.entries()) {
      const [ruleRegion, ruleModule, paramKey] = key.split(":") as [
        Region,
        ModuleType,
        string,
      ];
      if (ruleRegion !== region || ruleModule !== module) continue;
      if (!(paramKey in parameters)) continue;

      const violation = rule.check(parameters);
      if (violation) {
        violations.push(violation);
      }
    }
  }

  violations.sort((a, b) => {
    const order: Record<Severity, number> = { error: 0, warning: 1, info: 2 };
    return order[a.severity] - order[b.severity];
  });

  return violations;
}
