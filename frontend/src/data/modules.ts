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
  { id: 2, name: "Voltage Drop", discipline: "Electrical", standard: "IEC 60364-5-52" },
  { id: 3, name: "Maximum Demand", discipline: "Electrical", standard: "IEE / DEWA / IS 18-1" },
  { id: 4, name: "Short Circuit", discipline: "Electrical", standard: "IEC 60909" },
  { id: 5, name: "Lighting Design", discipline: "Electrical", standard: "EN 12464-1 / CIBSE" },
  { id: 6, name: "Power Factor Correction", discipline: "Electrical", standard: "IEC 60831" },
  { id: 7, name: "Generator Sizing", discipline: "Electrical", standard: "ISO 8528" },
  { id: 8, name: "UPS Sizing", discipline: "Electrical", standard: "IEC 62040" },
  { id: 9, name: "Panel Schedule", discipline: "Electrical", standard: "Multi-region" },
  { id: 10, name: "Cooling Load", discipline: "Mechanical", standard: "ASHRAE / CIBSE Guide A", path: "/calc/cooling-load" },
  { id: 11, name: "Duct Sizing", discipline: "Mechanical", standard: "ASHRAE / CIBSE Guide C" },
  { id: 12, name: "Heating Load", discipline: "Mechanical", standard: "EN 12831" },
  { id: 13, name: "Ventilation", discipline: "Mechanical", standard: "ASHRAE 62.1" },
  { id: 14, name: "Pipe Sizing", discipline: "Plumbing", standard: "BS EN 806 / IS 1172" },
  { id: 15, name: "Drainage Sizing", discipline: "Plumbing", standard: "BS EN 12056" },
  { id: 16, name: "Pump Sizing", discipline: "Plumbing", standard: "Darcy-Weisbach" },
  { id: 17, name: "Hot Water System", discipline: "Plumbing", standard: "BS EN 806-3" },
  { id: 18, name: "Rainwater Harvesting", discipline: "Plumbing", standard: "BS 8515 / AS 3500" },
  { id: 19, name: "Tank Sizing", discipline: "Plumbing", standard: "BS EN 806 / IS 1172" },
  { id: 20, name: "Sprinkler Design", discipline: "Fire", standard: "BS EN 12845 / NFPA 13" },
  { id: 21, name: "Fire Pump Sizing", discipline: "Fire", standard: "BS EN 12845 / NFPA 20" },
  { id: 22, name: "Fire Storage Tank", discipline: "Fire", standard: "BS 9251 / NBC 2016" },
  { id: 23, name: "Standpipe System", discipline: "Fire", standard: "NFPA 14 / BS 9990" },
  { id: 24, name: "BOQ Generator", discipline: "Reports", standard: "FIDIC / NRM2 / CPWD" },
  { id: 25, name: "Compliance Checker", discipline: "Reports", standard: "Regional limits" },
  { id: 26, name: "PDF Reports", discipline: "Reports", standard: "A4 calc sheets" },
];

export const DISCIPLINES = ["Electrical", "Mechanical", "Plumbing", "Fire", "Reports"] as const;

export const DISCIPLINE_META: Record<string, { icon: string; count: number }> = {
  Electrical: { icon: "⚡", count: 9 },
  Mechanical: { icon: "❄️", count: 4 },
  Plumbing: { icon: "🚰", count: 6 },
  Fire: { icon: "🔥", count: 4 },
  Reports: { icon: "📄", count: 3 },
};
