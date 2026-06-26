import styled from 'styled-components';
import { Bot } from 'lucide-react';

interface Props {
  onClick: () => void;
}

const AssistantButton = ({ onClick }: Props) => {
  return (
    <StyledWrapper>
      <button onClick={onClick} type="button" aria-label="Open AI assistant">
        <span>
          <Bot size={15} />
          Assistant
        </span>
      </button>
    </StyledWrapper>
  );
};

const StyledWrapper = styled.div`
  button {
    border: none;
    border-radius: 20px;
    background: linear-gradient(32deg, #03a9f4, #f441a5, #ffeb3b, #03a9f4);
    transition: all 1.5s ease;
    font-family: 'Ropa Sans', sans-serif;
    font-weight: bold;
    letter-spacing: 0.05rem;
    padding: 0;
    cursor: pointer;
  }
  button span {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    padding: 8px 16px;
    font-size: 14px;
    border-radius: 20px;
    background: #ffffff10;
    backdrop-filter: blur(20px);
    transition: 0.4s ease-in-out;
    transition-property: color, backdrop-filter;
    color: rgba(255, 255, 255, 0.9);
    height: 100%;
    width: 100%;
  }
  button span:hover {
    backdrop-filter: blur(0px);
    color: #ffffff;
  }
`;

export default AssistantButton;