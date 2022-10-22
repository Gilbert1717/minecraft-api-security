package net.zhuoweizhang.raspberryjuice;

import java.io.*;
import java.net.*;
import java.security.KeyPair;

public class ServerListenerThread implements Runnable {

	public ServerSocket serverSocket;

	public SocketAddress bindAddress;

	public boolean running = true;

	private RaspberryJuicePlugin plugin;

	private KeyPair RsaKeyPair;

	public ServerListenerThread(RaspberryJuicePlugin plugin, SocketAddress bindAddress, KeyPair RsaKeyPair) throws IOException {
		this.plugin = plugin;
		this.bindAddress = bindAddress;
		this.RsaKeyPair = RsaKeyPair;
		serverSocket = new ServerSocket();
		serverSocket.setReuseAddress(true);
		serverSocket.bind(bindAddress);
	}

	public void run() {
		while (running) {
			try {
				Socket newConnection = serverSocket.accept();
				if (!running) return;
				plugin.handleConnection(new RemoteSession(plugin, newConnection, RsaKeyPair));// pass keypair to RemoteSession
			} catch (Exception e) {
				// if the server thread is still running raise an error
				if (running) {
					plugin.getLogger().warning("Error creating new connection");
					e.printStackTrace();
				}
			}
		}
		try {
			serverSocket.close();
		} catch (Exception e) {
			plugin.getLogger().warning("Error closing server socket");
			e.printStackTrace();
		}
	}
}
