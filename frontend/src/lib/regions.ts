export interface Region {
  code: string;
  name: string;
  short: string;
  standard: string;
  flag: string;
}

export const REGIONS: Region[] = [
  { code: "gcc", name: "GCC (UAE · KSA · Qatar · Kuwait)", short: "GCC", standard: "BS 7671 / IEC 60364", flag: "🇦🇪" },
  { code: "europe", name: "Europe / United Kingdom", short: "Europe", standard: "BS 7671:2018+A2:2022", flag: "🇪🇺" },
  { code: "india", name: "India", short: "India", standard: "IS 3961 / IS 732", flag: "🇮🇳" },
  { code: "australia", name: "Australia / New Zealand", short: "Australia", standard: "AS/NZS 3008 / 3000", flag: "🇦🇺" },
];

export const CABLE_TYPES = [
  { value: "XLPE_CU", label: "XLPE Copper (90 °C)" },
  { value: "PVC_CU", label: "PVC Copper (70 °C)" },
  { value: "XLPE_AL", label: "XLPE Aluminium" },
];

export const INSTALL_METHODS = [
  { value: "C", label: "C — Clipped direct to surface" },
  { value: "E", label: "E — Free air on perforated tray" },
  { value: "B", label: "B — In conduit / trunking" },
  { value: "D", label: "D — Buried in ground" },
  { value: "F", label: "F — Touching cables on tray" },
];
