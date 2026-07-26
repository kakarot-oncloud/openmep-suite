export interface ModuleDef {
  id: number;
  name: string;
  discipline: "Electrical" | "Mechanical" | "Plumbing" | "Fire" | "Reports";
  standard: string;
  /** Route path if the calculator is live in this web app, else undefined. */
  path?: string;
}

export const MODULES: ModuleDef[] = [
  { id: 1, name: "Cable Sizing", discipline: "Electrical", standard: "BS 7671 / IEC 60364 / IS 3961 / AS 3008", path: "/calc/cable-sizing" },
  { id: 2, name: "Voltage Drop", discipline: "Electrical", standard: "IEC 60364-5-52", path: "/calc/voltage-drop" },
  { id: 3, name: "Maximum Demand", discipline: "Electrical", standard: "IEE / DEWA / IS 18-1", path: "/calc/maximum-demand" },
  { id: 4, name: "Short Circuit", discipline: "Electrical", standard: "IEC 60909", path: "/calc/short-circuit" },
  { id: 5, name: "Lighting Design", discipline: "Electrical", standard: "EN 12464-1 / CIBSE", path: "/calc/lighting" },
  { id: 6, name: "Power Factor Correction", discipline: "Electrical", standard: "IEC 60831", path: "/calc/pf-correction" },
  { id: 7, name: "Generator Sizing", discipline: "Electrical", standard: "ISO 8528", path: "/calc/generator-sizing" },
  { id: 8, name: "UPS Sizing", discipline: "Electrical", standard: "IEC 62040", path: "/calc/ups-sizing" },
  { id: 9, name: "Panel Schedule", discipline: "Electrical", standard: "Multi-region", path: "/calc/panel-schedule" },
  { id: 10, name: "Cooling Load", discipline: "Mechanical", standard: "ASHRAE / CIBSE Guide A", path: "/calc/cooling-load" },
  { id: 11, name: "Duct Sizing", discipline: "Mechanical", standard: "ASHRAE / CIBSE Guide C", path: "/calc/duct-sizing" },
  { id: 12, name: "Heating Load", discipline: "Mechanical", standard: "EN 12831", path: "/calc/heating-load" },
  { id: 13, name: "Ventilation", discipline: "Mechanical", standard: "ASHRAE 62.1", path: "/calc/ventilation" },
  { id: 14, name: "Pipe Sizing", discipline: "Plumbing", standard: "BS EN 806 / IS 1172", path: "/calc/pipe-sizing" },
  { id: 15, name: "Drainage Sizing", discipline: "Plumbing", standard: "BS EN 12056", path: "/calc/drainage-sizing" },
  { id: 16, name: "Pump Sizing", discipline: "Plumbing", standard: "Darcy-Weisbach", path: "/calc/pump-sizing" },
  { id: 17, name: "Hot Water System", discipline: "Plumbing", standard: "BS EN 806-3", path: "/calc/hot-water-system" },
  { id: 18, name: "Rainwater Harvesting", discipline: "Plumbing", standard: "BS 8515 / AS 3500", path: "/calc/rainwater-harvesting" },
  { id: 19, name: "Tank Sizing", discipline: "Plumbing", standard: "BS EN 806 / IS 1172", path: "/calc/tank-sizing" },
  { id: 20, name: "Sprinkler Design", discipline: "Fire", standard: "BS EN 12845 / NFPA 13", path: "/calc/sprinkler" },
  { id: 21, name: "Fire Pump Sizing", discipline: "Fire", standard: "BS EN 12845 / NFPA 20", path: "/calc/fire-pump" },
  { id: 22, name: "Fire Storage Tank", discipline: "Fire", standard: "BS 9251 / NBC 2016", path: "/calc/fire-tank" },
  { id: 23, name: "Standpipe System", discipline: "Fire", standard: "NFPA 14 / BS 9990", path: "/calc/standpipe" },
  { id: 24, name: "BOQ Generator", discipline: "Reports", standard: "FIDIC / NRM2 / CPWD", path: "/tools/boq" },
  { id: 25, name: "Compliance Checker", discipline: "Reports", standard: "Regional limits", path: "/tools/compliance" },
  { id: 26, name: "PDF Reports", discipline: "Reports", standard: "A4 calc sheets", path: "/tools/report" },
];

export const DISCIPLINES = ["Electrical", "Mechanical", "Plumbing", "Fire", "Reports"] as const;

export const DISCIPLINE_META: Record<string, { icon: string; count: number }> = {
  Electrical: { icon: "⚡", count: 9 },
  Mechanical: { icon: "❄️", count: 4 },
  Plumbing: { icon: "🚰", count: 6 },
  Fire: { icon: "🔥", count: 4 },
  Reports: { icon: "📄", count: 3 },
};
