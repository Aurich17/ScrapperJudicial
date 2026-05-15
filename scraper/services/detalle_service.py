from scraper.utils.constants import API_URL


def obtener_detalle_expediente(
    page,
    id_carpeta_judicial
):

    url = (
        f"{API_URL}/portadas/obtener-carpetas-judiciales"
        f"?idCarpetaJudicial={id_carpeta_judicial}"
    )

    data = page.evaluate(
        """
        async (url) => {

            const token = localStorage.getItem("token");

            const response = await fetch(url, {

                method: "GET",

                headers: {
                    "Authorization": `Bearer ${token}`,
                    "Content-Type": "application/json"
                }
            });

            return await response.json();
        }
        """,
        url
    )

    return data