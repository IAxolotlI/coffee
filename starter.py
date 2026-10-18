import requests
from uuid import uuid4


JsonObject = dict[str, object]


class CoffeeApiError(Exception):
    pass


class CoffeeNotFoundError(CoffeeApiError):
    pass


class SampleApisCoffeeClient:
    def __init__(
        self,
        base_url: str = "https://api.sampleapis.com/coffee/hot",
        timeout: float = 10.0,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    def list_drinks(self) -> list[JsonObject]:
        response = self._request("GET")
        try:
            data = response.json()
        except requests.exceptions.JSONDecodeError:
            raise CoffeeApiError("Неккоректный JSON")
        return data

    def get_drink(self, drink_id: int) -> JsonObject:
        response = self._request("GET", "/" + str(drink_id))
        try:
            data = response.json()
        except requests.exceptions.JSONDecodeError:
            raise CoffeeApiError("Неккоректный JSON")
        return data

    def create_drink(self, payload: JsonObject) -> JsonObject:
        response = self._request("POST", payload = payload)
        try:
            data = response.json()
        except requests.exceptions.JSONDecodeError:
            raise CoffeeApiError("Неккоректный JSON")
        return data

    def replace_drink(
        self,
        drink_id: int,
        payload: JsonObject,
    ) -> JsonObject:
        response = self._request("PUT", f"/{drink_id}", payload)
        try:
            data = response.json()
        except requests.exceptions.JSONDecodeError:
            raise CoffeeApiError("Некорректный JSON")
        return data

    def update_drink(
        self,
        drink_id: int,
        changes: JsonObject,
    ) -> JsonObject:
        response = self._request("PATCH", f"/{drink_id}", changes)
        try:
            data = response.json()
        except requests.exceptions.JSONDecodeError:
            raise CoffeeApiError("Некорректный JSON")
        return data

    def delete_drink(self, drink_id: int) -> None:   
        self._request("DELETE", f"/{drink_id}")

    def _request(
        self,
        method: str,
        path: str = "",
        payload: JsonObject | None = None,
    ) -> requests.Response:

        url = f"{self._base_url}{path}"

        try:
            response = requests.request(
                method=method,
                url=url,
                json=payload,
                timeout=self._timeout,
            )
        except requests.RequestException as error:
            raise CoffeeApiError(
                f"Сетевая ошибка при {method} {url}: {error}"
            ) from error

        if response.status_code == 404:
            raise CoffeeNotFoundError(
                f"{method} {url}: ресурс не найден (404)"
            )

        if not response.ok:
            raise CoffeeApiError(
                f"{method} {url}: HTTP {response.status_code}: "
                f"{response.text[:200]}"
            )

        content_type = response.headers.get("Content-Type", "")
        if "application/json" not in content_type.lower():
            raise CoffeeApiError(
                f"{method} {url}: ожидался JSON, "
                f"получен Content-Type={content_type!r}"
            )

        return response



def main() -> int:
    client = SampleApisCoffeeClient()
    marker = uuid4().hex[:8]
    created_id = None
    try:
        # GET коллекции.
        drinks = client.list_drinks()
        print(f"1. GET: {len(drinks)} напитков")

        # POST: исследуйте поля, добавьте marker в название.
        payload = {
            "title": f"Cffee {marker}",
            "description": "Hot drink",
            "ingredients": ["Water", "Coffee"],
            "image": "https://example.com/coffee.jpg",
        }
        created = client.create_drink(payload)
        created_id = created["id"]
        # Сразу сохраните id из ответа в created_id.
        print(f"2. POST: создан id={created_id}")

        # GET: сравните сохранённые поля с отправленными.
        fetched = client.get_drink(created_id)
        for field in ("title", "description", "ingredients", "image"):
            if fetched[field] != payload[field]:
                raise CoffeeApiError(f"GET: поле {field} не совпало")
        print("3. GET: поля совпали с отправленными")

        # PUT и повторный GET: проверьте все заменённые поля.
        replacement = {
            "title": f"Coffee {marker} (PUT)",
            "description": "Replaced via PUT",
            "ingredients": ["Water", "Coffee", "Secret"],
            "image": "https://example.com/coffee.jpg",
        }
        client.replace_drink(created_id, replacement)
        fetched = client.get_drink(created_id)
        for field in ("title", "description", "ingredients", "image"):
            if fetched[field] != replacement[field]:
                raise CoffeeApiError(f"PUT: поле {field} не заменилось")
        print("4. PUT: все поля заменены")

        # PATCH и повторный GET: проверьте изменённое поле
        # и убедитесь, что остальные поля сохранились.
        changes = {"description": "Patched by group"}
        client.update_drink(created_id, changes)
        fetched = client.get_drink(created_id)
        if fetched["description"] != changes["description"]:
            raise CoffeeApiError("PATCH: description не обновился")
        for field in ("title", "ingredients", "image"):
            if fetched[field] != replacement[field]:
                raise CoffeeApiError(f"PATCH: поле {field} не сохранилось")
        print("5. PATCH: изменилось только description")

        # DELETE и GET: убедитесь, что вернулся ожидаемый 404.
        client.delete_drink(created_id)
        try:
            client.get_drink(created_id)
        except CoffeeNotFoundError:
            print(f"6. DELETE: id={created_id} удалён, GET вернул 404")
        else:
            raise CoffeeApiError("DELETE: GET после удаления не вернул 404")

        # После подтверждения удаления: created_id = None.
        created_id = None
        print("Победа")
    except (CoffeeApiError, ValueError) as error:
        print(f"Ошибка: {error}. Метка группы: {marker}")
        return 1
    finally:
        if created_id is not None:
            try:
                client.delete_drink(created_id)
            except CoffeeNotFoundError:
                pass
            except CoffeeApiError as error:
                print(f"Не удалось удалить id={created_id}: {error}")
    return 0


if __name__ == "__main__":
    main()
