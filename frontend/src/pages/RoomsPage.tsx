import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "../api/client";
import { Building2, Check, X } from "lucide-react";

export const RoomsPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [selectedFloorId, setSelectedFloorId] = useState<number | null>(null);

  const { data: floors, isLoading } = useQuery({
    queryKey: ["floors"],
    queryFn: api.getFloors,
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: { rows_per_column?: number; is_active?: boolean } }) =>
      api.updateClassroom(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["floors"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard-stats"] });
    },
  });

  const activeFloor = floors?.find(f => selectedFloorId ? f.id === selectedFloorId : true) || floors?.[0];

  return (
    <div style={{ maxWidth: "1100px", margin: "0 auto", padding: "24px 28px" }}>
      {/* Page Title */}
      <div className="portal-page-header">
        <div>
          <h1 className="portal-page-title">Classroom & Floor Configuration</h1>
          <div style={{ fontSize: "13px", color: "#64748b", marginTop: "4px" }}>
            Manage examination halls across Ground, First, Second and Third floors
          </div>
        </div>
      </div>

      {isLoading && (
        <div style={{ padding: "40px", textAlign: "center", color: "#64748b" }}>
          Loading classrooms configuration...
        </div>
      )}

      {floors && (
        <>
          {/* Floor Navigation Tabs */}
          <div style={{ display: "flex", gap: "10px", marginBottom: "20px" }}>
            {floors.map((fl) => {
              const isSelected = activeFloor?.id === fl.id;
              const activeCount = fl.classrooms.filter(c => c.is_active).length;
              return (
                <button
                  key={fl.id}
                  onClick={() => setSelectedFloorId(fl.id)}
                  style={{
                    padding: "10px 18px",
                    borderRadius: "4px",
                    border: isSelected ? "2px solid #0050b3" : "1px solid #cbd5e1",
                    backgroundColor: isSelected ? "#0050b3" : "#ffffff",
                    color: isSelected ? "#ffffff" : "#1e293b",
                    fontFamily: "'Georgia', serif",
                    fontWeight: 700,
                    fontSize: "13px",
                    cursor: "pointer",
                    display: "flex",
                    alignItems: "center",
                    gap: "8px",
                    boxShadow: isSelected ? "0 2px 6px rgba(0, 80, 179, 0.25)" : "none",
                  }}
                >
                  <Building2 size={16} />
                  <span>{fl.name}</span>
                  <span
                    style={{
                      fontSize: "11px",
                      padding: "2px 6px",
                      borderRadius: "10px",
                      backgroundColor: isSelected ? "rgba(255,255,255,0.25)" : "#f1f5f9",
                      color: isSelected ? "#ffffff" : "#64748b",
                    }}
                  >
                    {activeCount}/{fl.classrooms.length} Halls
                  </span>
                </button>
              );
            })}
          </div>

          {/* Rooms Table Card */}
          {activeFloor && (
            <div
              style={{
                backgroundColor: "#ffffff",
                border: "1px solid #cbd5e1",
                borderRadius: "4px",
                padding: "24px",
                boxShadow: "0 2px 8px rgba(0,0,0,0.04)",
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
                <div>
                  <h3 style={{ fontFamily: "'Georgia', serif", fontSize: "16px", color: "#002f66", margin: 0 }}>
                    {activeFloor.name} Halls (Room Series: {activeFloor.classrooms[0]?.name} – {activeFloor.classrooms[activeFloor.classrooms.length - 1]?.name})
                  </h3>
                  <div style={{ fontSize: "12px", color: "#64748b", marginTop: "2px" }}>
                    Configure rows per column (6 or 7 rows) and enable/disable rooms for upcoming exams
                  </div>
                </div>

                <div style={{ fontSize: "12px", color: "#334155", fontWeight: 600 }}>
                  Floor Capacity: {activeFloor.classrooms.filter(r => r.is_active).reduce((sum, r) => sum + r.capacity, 0)} Seats
                </div>
              </div>

              <table className="portal-table">
                <thead>
                  <tr>
                    <th style={{ width: "120px" }}>Room No</th>
                    <th>Floor Level</th>
                    <th style={{ width: "130px", textAlign: "center" }}>Columns</th>
                    <th style={{ width: "160px", textAlign: "center" }}>Rows / Column</th>
                    <th style={{ width: "120px", textAlign: "center" }}>Capacity</th>
                    <th style={{ width: "140px", textAlign: "center" }}>Status</th>
                    <th style={{ width: "140px", textAlign: "center" }}>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {activeFloor.classrooms.map((room) => (
                    <tr key={room.id} style={{ opacity: room.is_active ? 1 : 0.65 }}>
                      {/* Room Name */}
                      <td className="mono-cell" style={{ fontSize: "14px", color: "#004a99" }}>
                        {room.name}
                      </td>

                      {/* Floor Name */}
                      <td>{activeFloor.name}</td>

                      {/* Columns */}
                      <td style={{ textAlign: "center" }}>
                        <span style={{ fontFamily: "monospace", fontWeight: 700 }}>4</span> (A, B, C, D)
                      </td>

                      {/* Rows Selector */}
                      <td style={{ textAlign: "center" }}>
                        <select
                          value={room.rows_per_column}
                          onChange={(e) => {
                            updateMutation.mutate({
                              id: room.id,
                              data: { rows_per_column: parseInt(e.target.value) },
                            });
                          }}
                          disabled={!room.is_active}
                          style={{
                            padding: "4px 8px",
                            borderRadius: "4px",
                            border: "1px solid #cbd5e1",
                            fontFamily: "'JetBrains Mono', monospace",
                            fontSize: "12px",
                            fontWeight: 700,
                            backgroundColor: "#f8fafc",
                            cursor: "pointer",
                          }}
                        >
                          <option value={6}>6 rows (A1..D6)</option>
                          <option value={7}>7 rows (A1..D7)</option>
                          <option value={8}>8 rows (A1..D8)</option>
                        </select>
                      </td>

                      {/* Capacity */}
                      <td style={{ textAlign: "center", fontWeight: 700, fontFamily: "monospace", fontSize: "13px" }}>
                        {room.capacity} seats
                      </td>

                      {/* Status */}
                      <td style={{ textAlign: "center" }}>
                        <span
                          style={{
                            display: "inline-flex",
                            alignItems: "center",
                            gap: "4px",
                            padding: "3px 8px",
                            borderRadius: "12px",
                            fontSize: "11px",
                            fontWeight: 700,
                            backgroundColor: room.is_active ? "#dcfce7" : "#f1f5f9",
                            color: room.is_active ? "#15803d" : "#64748b",
                          }}
                        >
                          {room.is_active ? <Check size={12} /> : <X size={12} />}
                          {room.is_active ? "ACTIVE" : "DISABLED"}
                        </span>
                      </td>

                      {/* Action toggle */}
                      <td style={{ textAlign: "center" }}>
                        <button
                          onClick={() => {
                            updateMutation.mutate({
                              id: room.id,
                              data: { is_active: !room.is_active },
                            });
                          }}
                          style={{
                            padding: "5px 12px",
                            borderRadius: "4px",
                            border: room.is_active ? "1px solid #cbd5e1" : "1px solid #16a34a",
                            backgroundColor: room.is_active ? "#ffffff" : "#16a34a",
                            color: room.is_active ? "#475569" : "#ffffff",
                            fontSize: "11px",
                            fontWeight: 700,
                            cursor: "pointer",
                            transition: "all 0.15s ease",
                          }}
                        >
                          {room.is_active ? "Disable Room" : "Enable Room"}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </div>
  );
};
