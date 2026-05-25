import { useState,useEffect, useRef } from "react";
import { sendMessage, resumeChat, fetchMessages } from "../api";
import { statusEnum, roleEnum } from "../enums/llm_response";
import SmartToyIcon from '@mui/icons-material/SmartToy';
import FaceIcon from '@mui/icons-material/Face';
import SendIcon from '@mui/icons-material/ArrowUpward';

export default function ChatBox({ threadId, setThreadId }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [waitingForResume, setWaitingForResume] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [isscroll, setIsScroll] = useState(false);

const chatBodyRef = useRef(null);

  const handleSend = async () => {

    if (!input.trim()) return;

    const userMessage = {
      role: roleEnum.USER,
      content: input,
      timestamp: new Date(),
      status: statusEnum.COMPLETED,
    };



    setMessages((prev) => [...prev, userMessage]);
    

    setInput("");
    try {
      setIsSending(true);
      let response;

      if (waitingForResume) {
        response = await resumeChat(threadId, input);
      } else {
        response = await sendMessage(input, threadId);
      }

      // console.log("API Response:", response);

      if (!threadId && response.thread_id) {
        setThreadId(response.thread_id);
        localStorage.setItem("threadId", response.thread_id);
      }

      setMessages((prev) => [
          ...prev,
          {
            role: roleEnum.AGENT,
            content: response.response,
            status: response.status,
            timestamp: response.timestamp || new Date(),
          },
        ]);
        setWaitingForResume(response.status === statusEnum.INTERRUPT);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: roleEnum.AGENT,
          content: "Server error.",
          status: statusEnum.COMPLETED,
          timestamp: response.timestamp || new Date(),
        },
      ]);
    }
    finally {
      setIsSending(false);
    }
  };

  const handleKeyDown = async (event) => {
    if (event.key === 'Enter') {
      await handleSend();
    }
  };

  const scrollToBottom = () => {
    const container = chatBodyRef.current;

    if (!container) return;

    container.scrollTop = container.scrollHeight;
  };

  useEffect(() => {
    async function fetchInitialMessages() {
      if(threadId) {
        let res = await fetchMessages(threadId);
        setMessages(() => [...res]);
      }
    }
    fetchInitialMessages();
  }, [threadId]);

  useEffect(() =>{
    if(isscroll) {
      return;
    }
    setTimeout(() => {
          scrollToBottom();
        }, 0);
  }, [messages]);

  const loadMoreMessages = async () => {
    if (!threadId || loadingMore || !hasMore) return;

    const container = chatBodyRef.current;
    const oldScrollHeight = container.scrollHeight;

    setLoadingMore(true);

    try {
      const res = await fetchMessages(threadId, page + 1, 15);

      if (!res || res.length === 0) {
        setHasMore(false);
        return;
      }

      setMessages((prev) => [...res, ...prev]);
      setPage((prev) => prev + 1);

      setTimeout(() => {
        const newScrollHeight = container.scrollHeight;
        container.scrollTop = newScrollHeight - oldScrollHeight;
      }, 0);
    } finally {
      setLoadingMore(false);
    }
  };

  const handleScroll = () => {
    const container = chatBodyRef.current;

    if (!container) return;

    if (container.scrollTop === 0) {
      setIsScroll(true);
      loadMoreMessages();
      setTimeout(() => setIsScroll(false), 100);
    }
  };

  return (

    <div className="container-fluid h-100 py-0 px-0">

      <div className="row d-flex justify-content-center h-100">
        <div className="col-md-12 col-lg-12 col-xl-12 ">

          <div className="card h-100" id="chat2">
            <div
              ref={chatBodyRef}
              onScroll={handleScroll}
              className="card-body"
              style={{
                position: "relative",
                height: "60vh",
                overflowY: "auto",
              }}
            >
              {loadingMore && (
                <div className="text-center text-muted small mb-2">
                  Loading older messages...
                </div>
              )}

              <div>
                {messages.map((msg, index) => (
                  <div
                    key={msg.id || index}
                    className={`d-flex flex-row justify-content-${
                      msg.role === roleEnum.USER ? "end" : "start"
                    }`}
                  >
                    {msg.role === roleEnum.AGENT && (
                      <SmartToyIcon style={{ width: "40px", height: "40px" }} />
                    )}

                    <div>
                      <p
                        className={`small p-2 ${
                          msg.role === roleEnum.USER
                            ? "text-white bg-primary"
                            : "bg-body-tertiary"
                        } rounded-3 ms-3 mb-1 text-start`}
                      >
                        {msg.content}
                      </p>

                      <p
                        className={`small ms-3 mb-3 rounded-3 text-muted d-flex justify-content-${
                          msg.role === roleEnum.USER ? "end" : "start"
                        }`}
                      >
                        {msg.timestamp
                          ? new Date(
                              typeof msg.timestamp === "string"
                                ? msg.timestamp.replace(" ", "T")
                                : msg.timestamp
                            ).toLocaleTimeString([], {
                              hour: "2-digit",
                              minute: "2-digit",
                            })
                          : ""}
                      </p>
                    </div>

                    {msg.role === roleEnum.USER && (
                      <FaceIcon
                        className="ms-3"
                        style={{ width: "40px", height: "40px" }}
                      />
                    )}
                  </div>
                ))}
              </div>
            </div>
            <div className="card-footer text-muted d-flex justify-content-start align-items-center p-3">
              <FaceIcon className="me-3" style={{width: "40px", height: "100%"}}/>
              <input type="text" className="form-control form-control-lg" id="exampleFormControlInput1"
                placeholder="Type message" value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={handleKeyDown}/>
              <button className="send-button ms-2" id="button-addon2" onClick={handleSend} disabled={isSending}><SendIcon style={{width: "20px", height: "20px", color:"black"}}/></button>
            </div>
          </div>

        </div>
      </div>

  </div>
  );
}