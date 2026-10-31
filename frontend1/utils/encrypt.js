// 简单的加密工具（实际项目中应使用更安全的加密方法）
export default {
	// 简单加密（Base64编码，实际应使用AES等）
	encrypt(text) {
		if (!text) return ''
		// 使用Base64编码（实际项目中应使用更安全的加密）
		return btoa(unescape(encodeURIComponent(text)))
	},
	
	// 解密
	decrypt(encryptedText) {
		if (!encryptedText) return ''
		try {
			return decodeURIComponent(escape(atob(encryptedText)))
		} catch (e) {
			return encryptedText
		}
	}
}

