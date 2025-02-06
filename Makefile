
NAME = ft_transcendence

all: $(NAME)

$(NAME):
	@echo "Building ft_transcendence"
	@docker compose up --build

clean:
	@echo "Cleaning ft_transcendence"
	@docker compose down

fclean: clean
	@echo "Removing ft_transcendence"
	@docker compose down --volumes

re: fclean all