export const CATEGORIES: Record<string, { label: string; bg: string }> = {
  festival: { label: "Festival", bg: "#FEF3C7" },
  concert: { label: "Concert", bg: "#FCE2E5" },
  soiree: { label: "Soirée", bg: "#FCE2E5" },
  conference: { label: "Conférence", bg: "#E3E0F3" },
  atelier: { label: "Atelier", bg: "#E3F2EA" },
  gastronomie: { label: "Gastronomie", bg: "#FDE8D7" },
  humour: { label: "Humour", bg: "#D9E4F5" },
  culture: { label: "Culture et traditions", bg: "#E3F2EA" },
  sport: { label: "Sport", bg: "#FEF3C7" },
  famille: { label: "Famille", bg: "#F3D9E2" },
  lancement: { label: "Lancement", bg: "#E8E1D3" },
  business: { label: "Business et networking", bg: "#E3E0F3" },
  religieux: { label: "Religieux", bg: "#E8E1D3" },
  salon: { label: "Salon et expo", bg: "#E3E0F3" },
};

export const catLabel = (k: string) => CATEGORIES[k]?.label ?? k;
export const catBg = (k: string) => CATEGORIES[k]?.bg ?? "#EEEEEE";
