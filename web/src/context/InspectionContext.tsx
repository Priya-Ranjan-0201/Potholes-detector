import React, { createContext, useContext, useState, useRef, useEffect } from "react";
import { detectDefects, InspectionResult, DetectionPreset } from "../utils/cvDetector";
import { useToast } from "./ToastContext";

export interface SampleImage {
  id: string;
  label: string;
  src: string;
  road: string;
  chainage?: string;
}

export const ROAD_SAMPLES: SampleImage[] = [
  {
    id: "capture-bengaluru",
    label: "Bengaluru Highway",
    src: "/samples/bengaluru_potholes.jpg",
    road: "Bengaluru Outer Ring Road",
    chainage: "ORR KM 24.6 (East Corridor)",
  },
  {
    id: "capture-pothole",
    label: "Asphalt Crater",
    src: "/samples/asphalt_crater.jpg",
    road: "State Highway 17 Pavement Crater",
    chainage: "SH-17 KM 88.2",
  },
  {
    id: "capture-cracks",
    label: "Alligator Cracks",
    src: "/samples/alligator_cracks.jpg",
    road: "Fatigue Alligator Pavement",
    chainage: "MDR-04 KM 12.1",
  },
  {
    id: "capture-mumbai",
    label: "Mumbai Expressway",
    src: "/samples/mumbai_potholes.avif",
    road: "Mumbai Urban Arterial Corridor",
    chainage: "Western Express Corridor KM 14.3",
  },
  {
    id: "capture-nh44",
    label: "NH-44 Highway",
    src: "/samples/pothole_nh44.jpg",
    road: "National Highway 44 (NH-44)",
    chainage: "NH-44 KM 312.4 (Northbound)",
  },
  {
    id: "capture-clean",
    label: "Clean Highway",
    src: "/samples/clean_road.jpg",
    road: "Clean Bituminous Highway Section",
    chainage: "NH-48 KM 45.0 (Passing Lane)",
  },
];

interface InspectionContextType {
  activeImageSrc: string;
  activeRoadName: string;
  activeChainage: string;
  selectedSampleId: string;
  preset: DetectionPreset;
  confThresh: number;
  inspection: InspectionResult;
  isScanning: boolean;
  scanStage: "preprocess" | "inference" | "postprocess";
  selectedBoxId: string | null;
  hoveredBoxId: string | null;
  showBoxes: boolean;
  uploadedFile: File | null;
  setPreset: (preset: DetectionPreset) => void;
  setConfThresh: (thresh: number) => void;
  setShowBoxes: (show: boolean) => void;
  setSelectedBoxId: (id: string | null | ((prev: string | null) => string | null)) => void;
  setHoveredBoxId: (id: string | null) => void;
  selectSample: (sample: SampleImage) => void;
  handleFileUpload: (file: File) => void;
  runDetection: (source?: string | Blob) => Promise<void>;
}

const InspectionContext = createContext<InspectionContextType | undefined>(undefined);

export const InspectionProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [activeImageSrc, setActiveImageSrc] = useState<string>("/samples/bengaluru_potholes.jpg");
  const [activeRoadName, setActiveRoadName] = useState<string>("Bengaluru Outer Ring Road");
  const [activeChainage, setActiveChainage] = useState<string>("ORR KM 24.6 (East Corridor)");
  const [selectedSampleId, setSelectedSampleId] = useState<string>("capture-bengaluru");
  const [preset, setPreset] = useState<DetectionPreset>("balanced");
  const [confThresh, setConfThresh] = useState<number>(0.25);
  const [showBoxes, setShowBoxes] = useState<boolean>(true);
  const [isScanning, setIsScanning] = useState<boolean>(false);
  const [scanStage, setScanStage] = useState<"preprocess" | "inference" | "postprocess">("postprocess");
  const [selectedBoxId, setSelectedBoxId] = useState<string | null>(null);
  const [hoveredBoxId, setHoveredBoxId] = useState<string | null>(null);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);

  const { error: showErrorToast } = useToast();
  const scanIdRef = useRef<number>(0);
  const abortRef = useRef<AbortController | null>(null);

  const [inspection, setInspection] = useState<InspectionResult>({
    source: "neural_api",
    totalDefects: 0,
    potholeCount: 0,
    crackCount: 0,
    maxSeverity: "Minor",
    overallScore: 100,
    boxes: [],
    latencyMs: 0,
    imageWidth: 640,
    imageHeight: 480,
    engine: "Unified YOLO11n-Rescue + Guarded Surface Prior",
  });

  const runDetection = async (sourceOverride?: string | Blob) => {
    const source = sourceOverride ?? (uploadedFile ?? activeImageSrc);
    if (!source) return;

    const scanId = ++scanIdRef.current;
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    setIsScanning(true);
    setSelectedBoxId(null);
    setHoveredBoxId(null);

    setInspection((prev) => ({
      ...prev,
      totalDefects: 0,
      potholeCount: 0,
      crackCount: 0,
      boxes: [],
      latencyMs: 0,
      error: undefined,
    }));

    try {
      const result = await detectDefects(
        source,
        confThresh,
        preset,
        (stage) => {
          if (scanIdRef.current === scanId) setScanStage(stage);
        },
        controller.signal
      );
      if (scanIdRef.current !== scanId) return;
      setInspection(result);
      if (result.error && !result.error.includes("Not a road photograph") && !result.error.includes("Image issue")) {
        showErrorToast("Inference Connection Error", result.error);
      }
    } catch (err) {
      if ((err as Error)?.name !== "AbortError") {
        console.error("Inference failed", err);
        showErrorToast("Inference Failed", (err as Error)?.message || "Backend unreachable");
      }
    } finally {
      if (scanIdRef.current === scanId) {
        setIsScanning(false);
      }
    }
  };

  useEffect(() => {
    if (activeImageSrc) {
      runDetection();
    }
  }, [activeImageSrc, confThresh, preset, selectedSampleId]);

  const selectSample = (sample: SampleImage) => {
    setUploadedFile(null);
    setSelectedSampleId(sample.id);
    setActiveImageSrc(sample.src);
    setActiveRoadName(sample.road);
    setActiveChainage(sample.chainage || "Highway Segment");
  };

  const handleFileUpload = (file: File) => {
    setUploadedFile(file);
    const url = URL.createObjectURL(file);
    setSelectedSampleId("");
    setActiveRoadName(file.name);
    setActiveChainage("User Uploaded Road Frame");
    setActiveImageSrc(url);
  };

  return (
    <InspectionContext.Provider
      value={{
        activeImageSrc,
        activeRoadName,
        activeChainage,
        selectedSampleId,
        preset,
        confThresh,
        inspection,
        isScanning,
        scanStage,
        selectedBoxId,
        hoveredBoxId,
        showBoxes,
        uploadedFile,
        setPreset,
        setConfThresh,
        setShowBoxes,
        setSelectedBoxId,
        setHoveredBoxId,
        selectSample,
        handleFileUpload,
        runDetection,
      }}
    >
      {children}
    </InspectionContext.Provider>
  );
};

export const useInspection = () => {
  const context = useContext(InspectionContext);
  if (!context) {
    throw new Error("useInspection must be used within an InspectionProvider");
  }
  return context;
};
