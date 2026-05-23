import { useState } from "react";
import ChatBox from "./components/ChatBox";
import Sidebar from "./components/SideBar";
import Topbar from "./components/TopBar";
import Dataset from "./components/Dataset";

function App() {
  const [activePage, setActivePage] = useState("chat");

  return (
    <div className="container-fluid px-0 d-flex flex-column" style={{ height: "100vh" }}>
      <Topbar activePage={activePage} setActivePage={setActivePage} />

      <div className="d-flex container-fluid px-0 h-100">
        <main className="flex-grow-1 d-flex">
          <Sidebar activePage={activePage} setActivePage={setActivePage} />

          <div className="container-fluid flex-grow-1 p-4 overflow-auto">
            {activePage === "chat" ? <ChatBox /> : <Dataset />}
          </div>
        </main>
      </div>
    </div>
  );
}

export default App;