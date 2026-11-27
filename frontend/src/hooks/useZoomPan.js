import { useState, useRef } from "react";

export function useZoomPan() {
  const [view, setView] = useState({ zoom: 1, x: 0, y: 0 });
  const [dragging, setDragging] = useState(false);
  const dragStart = useRef({ x: 0, y: 0 });
  const stageRef = useRef(null);

  const resetView = () => {
    setView({ zoom: 1, x: 0, y: 0 });
  };

  const applyZoom = (factor, mx = 0, my = 0) => {
    setView((prev) => {
      const nextZoom = Math.min(Math.max(prev.zoom * factor, 1), 6);
      if (nextZoom === prev.zoom) return prev;
      if (nextZoom <= 1.001) {
        return { zoom: 1, x: 0, y: 0 };
      }

      if (nextZoom > prev.zoom) {
        const ratio = nextZoom / prev.zoom;
        return {
          zoom: nextZoom,
          x: mx - (mx - prev.x) * ratio,
          y: my - (my - prev.y) * ratio,
        };
      }

      const t = (nextZoom - 1) / (prev.zoom - 1);
      return {
        zoom: nextZoom,
        x: prev.x * t,
        y: prev.y * t,
      };
    });
  };

  const handleWheel = (e, enabled) => {
    if (!enabled || !stageRef.current) return;
    const rect = stageRef.current.getBoundingClientRect();
    const mx = e.clientX - (rect.left + rect.width / 2);
    const my = e.clientY - (rect.top + rect.height / 2);
    const factor = e.deltaY < 0 ? 1.15 : 1 / 1.15;
    applyZoom(factor, mx, my);
  };

  const handleMouseDown = (e) => {
    if (view.zoom <= 1) return;
    setDragging(true);
    dragStart.current = { x: e.clientX - view.x, y: e.clientY - view.y };
  };

  const handleMouseMove = (e) => {
    if (!dragging) return;
    setView((prev) => ({
      ...prev,
      x: e.clientX - dragStart.current.x,
      y: e.clientY - dragStart.current.y,
    }));
  };

  const handleMouseUp = () => setDragging(false);

  return {
    zoom: view.zoom,
    pan: { x: view.x, y: view.y },
    stageRef,
    resetView,
    applyZoom,
    handleWheel,
    handleMouseDown,
    handleMouseMove,
    handleMouseUp,
  };
}