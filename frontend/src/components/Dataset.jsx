import { useEffect, useState } from "react";
import { fetchTables, fetchTableData } from "../api";
import StorageIcon from "@mui/icons-material/Storage";
import TableChartIcon from "@mui/icons-material/TableChart";
import ViewColumnIcon from "@mui/icons-material/ViewColumn";
import DatasetIcon from "@mui/icons-material/Dataset";

export default function Dataset({ threadId }) {
  const [tables, setTables] = useState([]);
  const [selectedTableData, setSelectedTableData] = useState(null);
  const [selectedTableName, setSelectedTableName] = useState("");

  useEffect(() => {
    async function fetchTablesL(threadId) {
      try {
        const tables = await fetchTables(threadId);
        // console.log("Fetched tables:", tables);
        setTables(tables);
      }
      catch (err) {
        console.error("Failed to fetch tables:", err);
      }
    }

    if (threadId) {
      fetchTablesL(threadId);
    }
  }, [threadId]);

  async function handleTableClick(tableName) {
    try {
      const data = await fetchTableData(threadId, tableName);
      // console.log(`Data for table ${tableName}:`, data);
      setSelectedTableData(data);
      setSelectedTableName(tableName);
    }
    catch (err) {
      console.error(`Failed to fetch data for table ${tableName}:`, err);
    }
  }

  function tablesExist() {
    return tables.length > 0;
  }

  const columnCount = selectedTableData?.columns?.length || 0;
  const rowCount = selectedTableData?.data?.length || 0;

  return (
    <div className="dataset-shell">
      <aside className="dataset-sidebar">
        <div className="dataset-sidebar__header">
          <DatasetIcon fontSize="small" />
          <div>
            <span>Dataset</span>
            <strong>{tables.length} tables</strong>
          </div>
        </div>

        <div className="dataset-table-list">
          {tables.map((tableName) => (
            <button
              key={tableName}
              className={`dataset-table-button ${selectedTableName === tableName ? "is-active" : ""}`}
              type="button"
              onClick={() => handleTableClick(tableName)}
            >
              <TableChartIcon fontSize="small" />
              <span>{tableName}</span>
            </button>
          ))}
        </div>
      </aside>

      {!tablesExist() && (
        <section className="dataset-empty-state">
          <StorageIcon />
          <h4>No tables found</h4>
          <p>Create a table from Chat to see it here.</p>
        </section>
      )}

      {tablesExist() && !selectedTableData && (
        <section className="dataset-empty-state">
          <TableChartIcon />
          <h4>No table selected</h4>
          <p>Select a table from the dataset panel to see it here.</p>
        </section>
      )}

      {selectedTableData && (
        <section className="dataset-detail">
          <header className="dataset-detail__header">
            <div>
              <span>Selected table</span>
              <h4>{selectedTableName || selectedTableData.name}</h4>
            </div>

            <div className="dataset-stats" aria-label="Table summary">
              <div>
                <TableChartIcon fontSize="small" />
                <strong>{rowCount}</strong>
                <span>Rows</span>
              </div>
              <div>
                <ViewColumnIcon fontSize="small" />
                <strong>{columnCount}</strong>
                <span>Columns</span>
              </div>
            </div>
          </header>

          <div className="dataset-matrix-stage">
            <div className="dataset-table-frame">
              <table className="dataset-data-table">
                <thead>
                  <tr>
                    {selectedTableData.columns.map((col, index) => (
                      <th key={index}>{col[0]}</th>
                    ))}
                  </tr>
                </thead>

                <tbody>
                  {selectedTableData.data.map((row, index) => (
                    <tr key={index}>
                      {row.map((cell, cellIndex) => (
                        <td key={cellIndex}>{cell}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </section>
      )}
    </div>
  );
}
