/**
 * Animated Message Circle Icon
 * Source: https://github.com/itshover/itshover
 */

import { forwardRef, useImperativeHandle } from "react";
import { AnimatedIconProps, AnimatedIconHandle } from "./types";
import { motion, useAnimate } from "motion/react";

const MessageCircleIcon = forwardRef<AnimatedIconHandle, AnimatedIconProps>(
  (
    { size = 24, color = "currentColor", strokeWidth = 2, className = "" },
    ref,
  ) => {
    const [scope, animate] = useAnimate();

    const start = async () => {
      animate(".message-path", { pathLength: 0, opacity: 0 }, { duration: 0 });

      await animate(
        ".message-path",
        { pathLength: [0, 1], opacity: [0, 1] },
        { duration: 0.6, ease: "easeInOut" },
      );

      animate(
        ".message-path",
        { scale: [1, 1.05, 1] },
        { duration: 0.3, ease: "easeOut" },
      );
    };

    const stop = () => {
      animate(
        ".message-path",
        { pathLength: 1, opacity: 1, scale: 1 },
        { duration: 0.2 },
      );
    };

    useImperativeHandle(ref, () => ({
      startAnimation: start,
      stopAnimation: stop,
    }));

    return (
      <motion.svg
        ref={scope}
        onHoverStart={start}
        onHoverEnd={stop}
        xmlns="http://www.w3.org/2000/svg"
        width={size}
        height={size}
        viewBox="0 0 24 24"
        fill="none"
        stroke={color}
        strokeWidth={strokeWidth}
        strokeLinecap="round"
        strokeLinejoin="round"
        className={`cursor-pointer ${className}`}
        style={{ overflow: "visible" }}
      >
        <motion.path
          className="message-path"
          d="M3 20l1.3-3.9C1.976 12.663 2.874 8.228 6.4 5.726c3.526-2.501 8.59-2.296 11.845.48 3.255 2.777 3.695 7.266 1.029 10.501-2.666 3.235-7.632 4.29-11.616 2.467L3 20"
          initial={{ pathLength: 1, opacity: 1 }}
          style={{ transformOrigin: "center" }}
        />
      </motion.svg>
    );
  },
);

MessageCircleIcon.displayName = "MessageCircleIcon";
export default MessageCircleIcon;
