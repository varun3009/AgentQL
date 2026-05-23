import { useState } from "react";
import { sendMessage, resumeChat } from "../api";
import { statusEnum } from "../enums/llm_response";
import SmartToyIcon from '@mui/icons-material/SmartToy';
import FaceIcon from '@mui/icons-material/Face';
import SendIcon from '@mui/icons-material/ArrowUpward';

export default function ChatBox() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [threadId, setThreadId] = useState(null);
  const [waitingForResume, setWaitingForResume] = useState(false);

  const handleSend = async () => {

    console.log("User Input:", input);
    if (!input.trim()) return;

    const userMessage = {
      role: "user",
      content: input,
    };

    setMessages((prev) => [...prev, userMessage]);

    try {
      let response;

      if (waitingForResume) {
        response = await resumeChat(threadId, input);
      } else {
        response = await sendMessage(input, threadId);
      }

      // console.log("API Response:", response);

      if (!threadId && response.thread_id) {
        setThreadId(response.thread_id);
      }

      setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: response.response,
          },
        ]);
        setWaitingForResume(response.status === statusEnum.INTERRUPT);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Server error.",
        },
      ]);
    }

    setInput("");
  };

  const handleKeyDown = async (event) => {
    console.log("Key Pressed:", event.key);
    if (event.key === 'Enter') {
      await handleSend();
    }
  };

  return (

    <div className="container-fluid h-100 py-0 px-0">

      <div className="row d-flex justify-content-center h-100">
        <div className="col-md-12 col-lg-12 col-xl-12 ">

          <div className="card h-100" id="chat2">
            <div className="card-body" data-mdb-perfect-scrollbar-init style={{position: "relative", height: "60vh"}}>

              <div className="d-flex flex-row justify-content-start">
                <SmartToyIcon style={{width: "40px", height: "100%"}}/>
                <div>
                  <p className="small p-2 ms-3 mb-1 rounded-3 bg-body-tertiary">What are you doing
                    tomorrow? Can we come up a bar?</p>
                  <p className="small ms-3 mb-3 rounded-3 text-muted text-start">23:58</p>
                </div>
              </div>

              <div className="d-flex flex-row justify-content-end mb-4 pt-1">
                <div>
                  <p className="small p-2 me-3 mb-1 text-white rounded-3 bg-primary">Long time no see! Tomorrow
                    office. will
                    be free on sunday.</p>
                  <p className="small me-3 mb-3 rounded-3 text-muted d-flex justify-content-end">00:06</p>
                </div>
                <FaceIcon style={{width: "40px", height: "100%"}}/>
              </div>
            </div>
            <div className="card-footer text-muted d-flex justify-content-start align-items-center p-3">
              <FaceIcon className="me-3" style={{width: "40px", height: "100%"}}/>
              <input type="text" className="form-control form-control-lg" id="exampleFormControlInput1"
                placeholder="Type message"/>
              <button className="send-button ms-2" id="button-addon2" disabled="true" onClick={handleSend}><SendIcon style={{width: "20px", height: "20px", color:"black"}}/></button>
            </div>
          </div>

        </div>
      </div>

  </div>
  );
}