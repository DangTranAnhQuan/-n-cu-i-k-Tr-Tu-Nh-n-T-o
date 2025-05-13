import pygame

class Button():
	def __init__(self, x, y, image, scale):
		width = image.get_width()
		height = image.get_height()
		self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)
		self.clicked = False

	def draw(self, surface):
		action = False
		
		pos = pygame.mouse.get_pos()
  
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				self.clicked = True
				action = True

		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False
		surface.blit(self.image, (self.rect.x, self.rect.y))
		return action

	def update_image(self, new_image):
		self.image_original = new_image
		width = self.image_original.get_width()
		height = self.image_original.get_height()
		self.scale = 0.55
		self.image = pygame.transform.scale(self.image_original, (int(width * self.scale), int(height * self.scale)))
		self.rect = self.image.get_rect(topleft=self.rect.topleft) 