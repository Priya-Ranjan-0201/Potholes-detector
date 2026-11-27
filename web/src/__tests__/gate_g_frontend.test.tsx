import { describe, it, expect } from "vitest";
import { TRANSLATIONS, LANGUAGES, LanguageCode } from "../context/LanguageContext";
import { readFileSync } from "fs";
import { resolve } from "path";

describe("Gate G — Frontend Design & Quality Verification", () => {
  it("enforces the Paper and Asphalt palette in tokens.css", () => {
    const tokensPath = resolve(process.cwd(), "src/styles/tokens.css");
    const content = readFileSync(tokensPath, "utf-8");

    // Light Paper Palette
    expect(content).toContain("#F6F4EE"); // light bg
    expect(content).toContain("#FFFFFF"); // light surface
    expect(content).toContain("#DAD6CA"); // light rule
    expect(content).toContain("#1B1A17"); // light text
    expect(content).toContain("#5F5B50"); // light muted
    expect(content).toContain("#E8B100"); // road-marking yellow accent
    expect(content).toContain("#1D4ED8"); // link

    // Dark Asphalt Palette
    expect(content).toContain("#121311"); // dark bg
    expect(content).toContain("#1A1B18"); // dark surface
    expect(content).toContain("#ECEAE2"); // dark text
    expect(content).toContain("#F5C400"); // dark accent

    // Colour-blind safe overlay colours
    expect(content).toContain("#D55E00"); // pothole
    expect(content).toContain("#0072B2"); // crack
    expect(content).toContain("#CC79A7"); // water-filled pothole

    // Radius (4-6px)
    expect(content).toContain("4px");
  });

  it("provides full navigation translations across all 6 required languages", () => {
    const requiredLangs: LanguageCode[] = ["en", "hi", "pa", "ta", "te", "bn"];
    expect(LANGUAGES.map((l) => l.code)).toEqual(expect.arrayContaining(requiredLangs));

    for (const lang of requiredLangs) {
      const dict = TRANSLATIONS[lang];
      expect(dict).toBeDefined();
      expect(dict.navHome).toBeTruthy();
      expect(dict.navDetect).toBeTruthy();
      expect(dict.navRecords).toBeTruthy();
      expect(dict.navReview).toBeTruthy();
      expect(dict.navBenchmarks).toBeTruthy();
      expect(dict.navMethod).toBeTruthy();
      expect(dict.footerNotice).toBeTruthy();
      if (lang === "en") {
        expect(dict.footerNotice).toContain("Student research project");
      }
    }
  });

  it("configures typography with Source Serif 4, IBM Plex Sans, and IBM Plex Mono in index.html", () => {
    const indexPath = resolve(process.cwd(), "index.html");
    const content = readFileSync(indexPath, "utf-8");

    expect(content).toContain("Source+Serif+4");
    expect(content).toContain("IBM+Plex+Sans");
    expect(content).toContain("IBM+Plex+Mono");
    expect(content).toContain("Noto+Sans");
  });

  it("verifies mandatory Rule R3 footer disclaimer", () => {
    const footerPath = resolve(process.cwd(), "src/components/Footer.tsx");
    const content = readFileSync(footerPath, "utf-8");

    expect(content).toContain(
      "Student research project. Not an official government system. Not safety-certified."
    );
  });
});
