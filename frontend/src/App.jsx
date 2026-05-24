import { useState, useEffect } from "react";
import ChatBox from "./components/ChatBox";
import Sidebar from "./components/SideBar";
import Topbar from "./components/TopBar";
import Dataset from "./components/Dataset";

function App() {
  const [activePage, setActivePage] = useState("chat");
  const [threadId, setThreadId] = useState(null);
  
  useEffect(() => {
    let storedThreadId = localStorage.getItem("threadId");
    if (storedThreadId) {
      setThreadId(storedThreadId);
    }
  },[])

  return (
    <div className="container-fluid px-0 d-flex flex-column" style={{ height: "100vh" }}>
      <Topbar activePage={activePage} setActivePage={setActivePage} />

      <div className="d-flex container-fluid px-0 h-100">
        <main className="flex-grow-1 d-flex">
          <Sidebar activePage={activePage} setActivePage={setActivePage} />

          <div className="container-fluid flex-grow-1 p-4 overflow-auto">
            {activePage === "chat" ? <ChatBox threadId={threadId} setThreadId={setThreadId} /> : <Dataset threadId={threadId} />}
          </div>
        </main>
      </div>
    </div>
  );
}

export default App;