import { contextBridge } from "electron";

contextBridge.exposeInMainWorld("odin", {
  platform: process.platform,
  version: "0.1.0",
});

export type OdinBridge = {
  platform: string;
  version: string;
};
