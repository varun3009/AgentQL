import StorageIcon from "@mui/icons-material/Storage";

export default function Dataset() {
  return (
    <div className="d-flex h-100 border rounded bg-white">
      <aside className="border-end p-3 bg-light" style={{ width: "260px" }}>
        <h5 className="mb-3">Tables</h5>
      </aside>

      <section className="flex-grow-1 d-flex flex-column align-items-center justify-content-center text-muted">
        <StorageIcon style={{ fontSize: 90 }} />
        <h4 className="mt-3">No tables found</h4>
        <p>Create a table from Chat to see it here.</p>
      </section>
    </div>
  );
}