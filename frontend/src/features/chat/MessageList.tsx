import type { PropsWithChildren } from "react";

const MessageList = ({ children }: PropsWithChildren) => {
  return <div className="message-list">{children}</div>;
};

export default MessageList;
