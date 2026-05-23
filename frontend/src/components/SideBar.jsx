import ChatIcon from "@mui/icons-material/Chat";
import StorageIcon from "@mui/icons-material/Storage";

export default function Sidebar({ activePage, setActivePage }) {
    console.log("Active Page:", activePage);
    console.log("Set Active Page Function:", setActivePage);
  return (
    <aside className="bg-dark text-white p-3 d-flex flex-column justify-content-center" style={{ width: "60px" }}>

      <button
        className={`nav-button w-100 mb-3 px-0 py-0 ${
          activePage === "chat" ? "active" : ""
        }`}
        onClick={() => setActivePage("chat")}
        aria-current={activePage === "chat" ? "page" : undefined}
      >
        <ChatIcon fontSize="small"  />
      </button>

      <button
        className={`nav-button w-100 px-0 py-0 ${
          activePage === "dataset" ? "active" : ""
        }`}
        onClick={() =>  setActivePage("dataset")}
        aria-current={activePage === "dataset" ? "page" : undefined}
      >
        <StorageIcon fontSize="small"/>
      </button>
    </aside>
  );
}