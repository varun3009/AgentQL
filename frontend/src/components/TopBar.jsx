export default function Topbar({ activePage, setActivePage }) {
  return (
    <nav className="navbar bg-light border-bottom px-4 w-100 justify-space-between">
      <span className="navbar-brand mb-0 h1">
        AgentQL
      </span>
      <div className="d-flex gap-3">
        <button
          className={`nav-button w-100 text-start px-0 py-0 ${
            activePage === "chat" ? "active border-bottom border-3" : ""
          }`}
          onClick={() => setActivePage && setActivePage("chat")}
          aria-current={activePage === "chat" ? "page" : undefined}
        >
          Chat
        </button>

        <button
          className={`nav-button w-100 text-start px-0 py-0 ${
            activePage === "dataset" ? "active border-bottom border-3" : ""
          }`}
          onClick={() => setActivePage && setActivePage("dataset")}
          aria-current={activePage === "dataset" ? "page" : undefined}
        >
          Dataset
        </button>
      </div>
      <span>GitHub</span>
    </nav>
  );
}